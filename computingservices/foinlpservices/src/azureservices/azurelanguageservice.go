package azureservices

import (
	"bytes"
	"encoding/json"
	"fmt"
	"foinlpservice/solrsearchservices"
	"foinlpservice/types"
	"log"
	"net/http"
)

func IdentifyPII(data types.AzureEventGridMessage) {
	// Sample text for PII detection
	// text := "John Doe, a 35-year-old software engineer, lives at 1234 Elm Street, Springfield, Ontario, M5A 1A1. His phone number is (555) 123-4567, and his email address is johndoe@example.com. He was born on March 14, 1988, and holds a Canadian passport with the number X1234567. His employee ID at Acme Corp. is 8765. John’s credit card number is 4111 2222 3333 4444, and his Canadian SIN is 123 456 789. His health insurance ID is HI987654321"

	document := solrsearchservices.GetSolrDocumentByID(data.Foisolrid)
	text := document.Text[0]

	// Prepare the request payload
	payload := types.RequestPayload{
		Documents: []types.Document{
			{
				ID:       "1",
				Text:     text,
				Language: "en",
			},
		},
	}

	// Marshal the payload into JSON
	payloadBytes, err := json.Marshal(payload)
	if err != nil {
		log.Fatalf("Failed to marshal payload: %v", err)
	}

	// Create a new HTTP request
	req, err := http.NewRequest("POST", endpoint+"text/analytics/v3.1/entities/recognition/pii", bytes.NewBuffer(payloadBytes))
	if err != nil {
		log.Fatalf("Failed to create request: %v", err)
	}

	// Set headers
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Ocp-Apim-Subscription-Key", apiKey)

	// Send the request
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		log.Fatalf("Failed to send request: %v", err)
	}
	defer resp.Body.Close()

	// Check the response status code
	if resp.StatusCode != http.StatusOK {
		log.Fatalf("Request failed with status code: %d", resp.StatusCode)
	}

	// Decode the response
	var result types.ResponsePayload
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		log.Fatalf("Failed to decode response: %v", err)
	}

	// Print the detected PII entities
	for _, doc := range result.Documents {
		fmt.Printf("Document ID: %s\n", doc.ID)
		for _, entity := range doc.Entities {
			fmt.Printf("Entity: %s, Category: %s, SubCategory: %s, Confidence Score: %.2f\n",
				entity.Text, entity.Category, entity.SubCategory, entity.ConfidenceScore)
		}
	}
}
