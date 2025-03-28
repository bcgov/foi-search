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
)

func PushtoEventGrid(events []types.EventGridEvent) bool {
	eventGridTopicURL := utils.ViperEnvVariable("azureeventgridendpoint")
	accessKey := utils.ViperEnvVariable("azureeventgridaccesskey")

	// Prepare the event in JSON format
	eventJSON, err := json.Marshal(events)
	if err != nil {
		log.Fatalf("Error marshaling event: %v", err)
	}

	// Create the HTTP request
	req, err := http.NewRequest("POST", eventGridTopicURL, bytes.NewBuffer(eventJSON))
	if err != nil {
		log.Fatalf("Error creating HTTP request: %v", err)
	}

	// Set headers, including the Access Key for authentication
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("aeg-sas-key", accessKey)

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
		return true
	} else {
		log.Fatalf("Failed to push event. Status: %s, Response: %s\n", resp.Status, body)
		return false
	}
}
