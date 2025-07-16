package azureservices

import (
	"bytes"
	"encoding/json"
	"foinlpservice/types"
	"foinlpservice/utils"
	"io"
	"log"
	"net/http"
)

func IdentifyPII(text string, client *http.Client) string {
	endpoint := utils.ViperEnvVariable("azurelanguageserviceendpoint")
	apiKey := utils.ViperEnvVariable("azureapikey")

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

	resp, err := client.Do(req)
	if err != nil {
		log.Fatalf("Failed to send request: %v", err)
	}
	// log.Printf("received request")
	defer resp.Body.Close()

	// Check the response status code
	if resp.StatusCode != http.StatusOK {
		log.Fatalf("Request failed with status code: %d", resp.StatusCode)
	}

	jsonBytes, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Fatalf("Failed to read response body: %v", err)
	}

	jsonString := string(jsonBytes) // Convert bytes to string

	return jsonString

}
