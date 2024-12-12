package azureservices

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
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
func (a *AzureService) AnalyzeAndExtractDocument(jsonPayload []byte) error {
	requestURL := fmt.Sprintf("%s/formrecognizer/documentModels/prebuilt-read:analyze?api-version=2023-07-31&stringIndexType=utf16CodeUnit", a.BaseURL)
	// Send the POST request
	apimRequestID, err := a.createAnalysisRequest(requestURL, jsonPayload)
	if err != nil {
		return fmt.Errorf("failed to initiate document analysis: %w", err)
	}
	results, err := a.getAnalysisResults(apimRequestID)
	if err != nil {
		return fmt.Errorf("failed to fetch analysis results: %w", err)
	}
	//Print extracted data form document
	fmt.Printf("Analysis Results: %v\n", results)
	return nil
}

// sendAnalyzeRequest sends the initial analysis request to the Azure API
func (a *AzureService) createAnalysisRequest(requestURL string, jsonPayload []byte) (string, error) {
	req, err := http.NewRequest(http.MethodPost, requestURL, bytes.NewBuffer(jsonPayload))
	if err != nil {
		return "", fmt.Errorf("failed to create POST request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Ocp-Apim-Subscription-Key", a.SubscriptionKey)
	res, err := a.Client.Do(req)
	if err != nil {
		return "", fmt.Errorf("error making HTTP request: %w", err)
	}
	defer res.Body.Close()
	if res.StatusCode != http.StatusOK {
		return "", fmt.Errorf("unexpected response status: %s", res.Status)
	}
	apimRequestID := res.Header.Get("Apim-Request-Id")
	if apimRequestID == "" {
		return "", fmt.Errorf("missing Apim-Request-Id in response header")
	}
	return apimRequestID, nil
}

func (a *AzureService) getAnalysisResults(apimRequestID string) (map[string]interface{}, error) {
	extractReqURL := fmt.Sprintf(
		"%s/formrecognizer/documentModels/prebuilt-read/analyzeResults/%s?api-version=2023-07-31",
		a.BaseURL, apimRequestID,
	)
	for {
		time.Sleep(1 * time.Second)
		jsonResponse, err := a.getExtractedResults(extractReqURL)
		if err != nil {
			return nil, err
		}
		status, ok := jsonResponse["status"].(string)
		if !ok {
			return nil, fmt.Errorf("missing or invalid 'status' in response")
		}
		fmt.Printf("Current status: %s\n", status)
		switch status {
		case "succeeded":
			return jsonResponse, nil
		case "running":
			continue
		default:
			return nil, fmt.Errorf("analysis failed with status: %s", status)
		}
	}
}

// Helper function to perform the HTTP GET request and parse the JSON response
func (a *AzureService) getExtractedResults(url string) (map[string]interface{}, error) {
	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create GET request: %w", err)
	}
	req.Header.Set("Ocp-Apim-Subscription-Key", a.SubscriptionKey)
	res, err := a.Client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("error making HTTP request: %w", err)
	}
	defer res.Body.Close()
	if res.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("unexpected response status: %s", res.Status)
	}
	bodyBytes, err := io.ReadAll(res.Body)
	if err != nil {
		return nil, fmt.Errorf("error reading response body: %w", err)
	}
	var jsonResponse map[string]interface{}
	err = json.Unmarshal(bodyBytes, &jsonResponse)
	if err != nil {
		return nil, fmt.Errorf("error unmarshaling response body: %w", err)
	}
	return jsonResponse, nil
}
