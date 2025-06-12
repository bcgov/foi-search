package main

import (
	"azuredocextractservice/azureservices"
	"azuredocextractservice/httpservices"
	"azuredocextractservice/s3services"
	"azuredocextractservice/solrsearchservices"
	"azuredocextractservice/types"
	"azuredocextractservice/utils"
	"fmt"
	"log"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/google/uuid"
)

type AzureExtract struct {
	status        string
	analyzeResult string
}

func main() {

	start := time.Now()

	logfilepath := utils.ViperEnvVariable("logfilepath")
	file, err := os.OpenFile(logfilepath+start.Format("2006-01-02")+"docextractlog.txt", os.O_WRONLY|os.O_CREATE|os.O_APPEND, 0644)

	if err != nil {
		fmt.Println("Error opening file:", err)
		return
	}
	defer file.Close()

	// Redirect stdout to the file.
	os.Stdout = file

	fmt.Println("\nStart Time :" + start.String())
	dequeuedmessages, err := httpservices.ProcessMessage()
	if err != nil {
		log.Fatalf("Error fetching messages: %v", err)
	}
	// Print each message
	for _, message := range dequeuedmessages {
		fmt.Printf("Received message: %+v", message)

		var requests []types.Requests = message.Requests

		for _, request := range requests {
			for _, document := range request.Documents {
				var parsedURL = document.DocumentS3URL
				var jsonStrbytes []byte = getBytesfromDocumentPath(parsedURL)
				analysisResults, _analyzeerr := azureservices.CallAzureDocument(jsonStrbytes, document, request)
				if _analyzeerr != nil {
					fmt.Printf("Skipping document ID - %v (request ID - %v) due to error: %v", document.DocumentID, request.MinistryRequestID, _analyzeerr)
					continue // Move to the next document
				} else if analysisResults.Status == "succeeded" {
					searchdocumentpagelines := []types.SOLRSearchDocument{}
					//PUSH to solr.
					for _, page := range analysisResults.AnalyzeResult.Pages {
						for _, line := range page.Lines {
							receviedDate, timeparseerror := time.Parse(time.RFC3339, request.ReceivedDate)
							if timeparseerror != nil {
								fmt.Println("Error parsing custom date-time:", timeparseerror)
							}
							newUUID := uuid.New()
							_solrsearchdocuemnt := types.SOLRSearchDocument{
								Foisolrid:              newUUID.String(),
								FoiDocumentID:          strconv.Itoa(int(document.DocumentID)),
								FoiRequestNumber:       request.RequestNumber,
								FoiMinistryRequestID:   request.MinistryRequestID,
								FoiMinistryCode:        request.MinistryCode,
								FoiDocumentFileName:    document.DocumentName,
								FoiDocumentPageNumber:  page.PageNumber,
								FoiDocumentSentence:    line.Content,
								FoiRequestMiscInfo:     request.RequestMiscInfo,
								FoiRequestReceivedDate: receviedDate,
								FoiDocumentURL:         document.DocumentS3URL,
								FoiRequestType:         request.RequestType,
							}
							searchdocumentpagelines = append(searchdocumentpagelines, _solrsearchdocuemnt)
							fmt.Println(_solrsearchdocuemnt.FoiDocumentFileName)
						}

					}

					solrsearchservices.PushtoSolr(searchdocumentpagelines)

				}
			}
		}

		// Get the path after the hostname

		fmt.Printf("################-------------------------------####################")
	}
	end := time.Now()
	fmt.Println("End Time :" + end.String())
	total := end.Sub(start)
	fmt.Println("Total time:" + total.String())
}

func getBytesfromDocumentPath(documenturlpath string) []byte {
	//path := strings.TrimPrefix(documenturlpath, "/")
	//bucketName, relativePath, found := strings.Cut(path, "/")
	parsedURL, err := url.Parse(documenturlpath)
	if err != nil {
		fmt.Println("Error is parsing URL")
		return nil
	}
	relativePath := parsedURL.Path
	relativePath = strings.TrimPrefix(relativePath, "/")
	bucketName, relativePath, found := strings.Cut(relativePath, "/")
	if !found {
		fmt.Println("Invalid URL format")
		return nil
	}
	fmt.Printf("Bucket: %s, Key: %s", bucketName, relativePath)
	var s3url = s3services.GetFilefroms3(relativePath, bucketName)
	jsonStr := `{
			"urlSource": "` + s3url + `"
		}`
	var jsonStrbytes = []byte(jsonStr)

	return jsonStrbytes
}
