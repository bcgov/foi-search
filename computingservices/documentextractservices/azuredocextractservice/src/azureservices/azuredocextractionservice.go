package azureservices

import (
	"azuredocextractservice/docreviewerauditservice"
	"azuredocextractservice/types"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strconv"
	"time"
)

// AzureService handles interactions with Azure Form Recognizer API
type AzureService struct {
	SubscriptionKey string
	BaseURL         string
	Client          http.Client
}

// NewAzureService initializes a new AzureService instance
func NewAzureService(subscriptionKey string, baseURL string) *AzureService {
	return &AzureService{
		SubscriptionKey: subscriptionKey,
		BaseURL:         baseURL,
		Client: http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// CallAzureDocument initiates the document analysis request
func (a *AzureService) AnalyzeAndExtractDocument(jsonPayload []byte, document types.Documents, request types.Requests) (types.AnalyzeResults, error) {

	var results types.AnalyzeResults
	requestURL := fmt.Sprintf("%s/formrecognizer/documentModels/prebuilt-read:analyze?api-version=2023-07-31&stringIndexType=utf16CodeUnit", a.BaseURL)
	// Send the POST request
	apimRequestID, err := a.createAnalysisRequest(requestURL, jsonPayload)
	if err != nil {
		return results, fmt.Errorf("failed to initiate document analysis: %w", err)
	} else {
		wrapDocReviewerAudit(document.DocumentID, request.MinistryRequestID, apimRequestID, "azureextractrequestcreated")
	}

	results, error := a.getAnalysisResults(apimRequestID, document.DocumentID, request.MinistryRequestID)
	if error != nil {
		return results, fmt.Errorf("failed to fetch analysis results: %v", error)
	}
	//Print extracted data form document
	fmt.Printf("Reached end of analysis results\n")
	return results, err
}

// sendAnalyzeRequest sends the initial analysis request to the Azure API
func (a *AzureService) createAnalysisRequest(requestURL string, jsonPayload []byte) (string, error) {

	req, _ := http.NewRequest(http.MethodPost, requestURL, bytes.NewBuffer(jsonPayload))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Ocp-Apim-Subscription-Key", a.SubscriptionKey)
	res, err := a.Client.Do(req)
	if err != nil {
		return "", fmt.Errorf("error making HTTP request: %w", err)
	}
	defer res.Body.Close()
	apimRequestID := res.Header.Get("Apim-Request-Id")

	if apimRequestID == "" {
		return "", fmt.Errorf("missing Apim-Request-Id in response header")
	}
	return apimRequestID, nil
}

func (a *AzureService) getAnalysisResults(apimRequestID string, documentid int64, ministryrequestid string) (types.AnalyzeResults, error) {
	extractReqURL := fmt.Sprintf(
		"%s/formrecognizer/documentModels/prebuilt-read/analyzeResults/%s?api-version=2023-07-31",
		a.BaseURL, apimRequestID,
	)

	for {
		time.Sleep(1 * time.Second)
		result, err := a.getExtractedResults(extractReqURL)
		if err != nil {
			return result, err
		}

		status := result.Status
		fmt.Printf("Current status: %s\n", result.Status)
		switch status {
		case "succeeded":
			wrapDocReviewerAudit(documentid, ministryrequestid, apimRequestID, "extractionsucceeded")
			return result, nil
		case "running":
			wrapDocReviewerAudit(documentid, ministryrequestid, apimRequestID, "extractionjobrunning")
			continue
		default:
			wrapDocReviewerAudit(documentid, ministryrequestid, apimRequestID, "extractionjobfailed")
			return result, fmt.Errorf("analysis failed with status: %s", status)
		}
	}
}

// Helper function to perform the HTTP GET request and parse the JSON response
func (a *AzureService) getExtractedResults(url string) (types.AnalyzeResults, error) {
	var result types.AnalyzeResults
	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		return result, fmt.Errorf("failed to create GET request: %w", err)
	}
	req.Header.Set("Ocp-Apim-Subscription-Key", a.SubscriptionKey)
	res, err := a.Client.Do(req)
	if err != nil {
		return result, fmt.Errorf("error making HTTP request: %w", err)
	}
	defer res.Body.Close()
	fmt.Println("Response status code:", res.StatusCode)
	if res.StatusCode != http.StatusOK {
		return result, fmt.Errorf("unexpected response status: %s", res.Status)
	}
	bodyBytes, err := io.ReadAll(res.Body)
	if err != nil {
		return result, fmt.Errorf("error reading response body: %w", err)
	}
	// fmt.Println("Response Body starts here:")
	// fmt.Println(string(bodyBytes))
	fmt.Println("Response Body ends here:")
	// var jsonResponse map[string]interface{}
	// json.Unmarshal(bodyBytes, &jsonResponse)
	err = json.Unmarshal(bodyBytes, &result)
	if err != nil {
		return result, fmt.Errorf("error unmarshaling response body: %w", err)
	}
	return result, nil
}

func wrapDocReviewerAudit(documentid int64, ministryrequestidrequest string, apimRequestID string, status string) bool {
	ministryrequestid, minreqidconerr := strconv.ParseInt(ministryrequestidrequest, 10, 64)
	if minreqidconerr != nil {
		fmt.Sprint("Error while converting ministry request ID")
	}
	docreviewaudit := types.DocReviewAudit{DocumentID: documentid, MinistryRequestID: ministryrequestid,
		Description: fmt.Sprintf(`{apimRequestID:%v}`, apimRequestID), Status: status}
	returnstate := docreviewerauditservice.PushtoDocReviewer(docreviewaudit)
	return returnstate
}
