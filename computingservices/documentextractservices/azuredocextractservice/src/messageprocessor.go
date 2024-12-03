package main

import (
	"azuredocextractservice/azureservices"
	"azuredocextractservice/httpservices"
	"azuredocextractservice/s3services"
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
		// jsonstr := `{
		// 	"urlSource": "` + message.S3URI + `"
		// }`
		// fmt.Printf("json url str formated %s\n", jsonstr)
		//var jsonStrbytes = []byte(jsonstr)
		//var s3url = s3services.GetFilefroms3("ORIGINALPDF.pdf", "test123")
		// fmt.Printf("MinistryRequestId: %s, RequestNumber: %s, Host: %s\n", message.MinistryRequestId,
		// 	message.RequestNumber, message.DivisionName)
		parsedURL, err := url.Parse(message.S3Uri)
		if err != nil {
			fmt.Printf("Error parsing URL: %v\n", err)
			return
		}
		// Get the path after the hostname
		path := strings.TrimPrefix(parsedURL.Path, "/")
		bucketName, relativePath, found := strings.Cut(path, "/")
		if !found {
			fmt.Println("Invalid URL format")
			return
		}
		fmt.Printf("Bucket: %s, Key: %s\n", bucketName, relativePath)
		var s3url = s3services.GetFilefroms3(relativePath, bucketName)
		jsonStr := `{
			"urlSource": "` + s3url + `"
		}`
		var jsonStrbytes = []byte(jsonStr)
		azureservices.CallAzureDocument(jsonStrbytes)
		fmt.Printf("################-------------------------------####################")
	}
	end := time.Now()
	fmt.Println("End Time :" + end.String())
	total := end.Sub(start)
	fmt.Println("Total time:" + total.String())
}
