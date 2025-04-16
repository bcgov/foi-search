package azureservices

import (
	"azuredocextractservice/types"
	"azuredocextractservice/utils"
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"time"
)

func PushtoEventGrid(events []types.AzureEventGridMessage) bool {
	eventGridTopicURL := utils.ViperEnvVariable("azureeventgridendpoint")
	accessKey := utils.ViperEnvVariable("azureeventgridaccesskey")

	for _, event := range events {
		cloudEvent := types.CloudEvent{
			ID:              event.FoiDocumentID,
			Source:          "pii",
			Subject:         "pii",
			SpecVersion:     "1.0",
			Data:            event,
			DataContentType: "application/json",
			Type:            "pii",
			Time:            time.Now().Format(time.RFC3339),
		}

		// Prepare the event in JSON format
		eventJSON, err := json.Marshal(cloudEvent)
		if err != nil {
			log.Fatalf("Error marshaling event: %v", err)
		}

		// Create the HTTP request
		req, err := http.NewRequest("POST", eventGridTopicURL, bytes.NewBuffer(eventJSON))
		if err != nil {
			log.Fatalf("Error creating HTTP request: %v", err)
		}

		// Set headers, including the Access Key for authentication

		req.Header.Set("Content-Type", "application/cloudevents+json")
		req.Header.Set("Authorization", "SharedAccessKey "+accessKey)

		// Send the request
		client := &http.Client{}
		resp, err := client.Do(req)
		if err != nil {
			log.Fatalf("Error sending request: %v", err)
		}
		defer resp.Body.Close()

		// Read the response body
		body, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			log.Fatalf("Error reading response: %v", err)
		}

		// Log the response
		if resp.StatusCode == http.StatusOK {
			fmt.Println("Event successfully pushed to Event Grid!")
		} else {
			log.Fatalf("Failed to push event. Status: %s, Response: %s\n", resp.Status, body)
			return false
		}
	}
	return true
}
