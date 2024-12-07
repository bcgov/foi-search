package azureservices

import (
	"log"
)

func CallAzureDocument(jsonPayload []byte) {
	subscriptionKey := "abcd"
	baseURL := "https://foidocintelservice.cognitiveservices.azure.com"

	service := NewAzureService(subscriptionKey, baseURL)

	// Example JSON payload
	//jsonPayload := []byte(`{"url": "https://example.com/sample.pdf"}`)

	err := service.AnalyzeAndExtractDocument(jsonPayload)
	if err != nil {
		log.Fatalf("Error calling Azure Document API: %v", err)
	}
}
