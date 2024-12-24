package main

import (
	"azuredocextractservice/azureservices"
	"azuredocextractservice/httpservices"
	"azuredocextractservice/s3services"
	"azuredocextractservice/types"
	"fmt"
	"log"
	"net/url"
	"strings"
	"time"
)

type AzureExtract struct {
	status        string
	analyzeResult string
}

func main() {

	start := time.Now()
	fmt.Println("Start Time :" + start.String())
	dequeuedmessages, err := httpservices.ProcessMessage()
	if err != nil {
		log.Fatalf("Error fetching messages: %v", err)
	}
	// Print each message
	for _, message := range dequeuedmessages {
		fmt.Printf("Received message: %+v\n", message)

		var requests []types.Requests = message.Requests

		for _, request := range requests {
			for _, document := range request.Documents {
				var parsedURL = document.DocumentS3URL
				var jsonStrbytes []byte = getBytesfromDocumentPath(parsedURL)
				analysisResults, _analyzeerr := azureservices.CallAzureDocument(jsonStrbytes)
				if _analyzeerr != nil {
					//pUSH to solr.
					//analysisResults.AnalyzeResult.Pages
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
	fmt.Printf("Bucket: %s, Key: %s\n", bucketName, relativePath)
	var s3url = s3services.GetFilefroms3(relativePath, bucketName)
	jsonStr := `{
			"urlSource": "` + s3url + `"
		}`
	var jsonStrbytes = []byte(jsonStr)

	return jsonStrbytes
}
