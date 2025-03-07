package main

import (
	"encoding/json"
	"fmt"
	"foinlpservice/azureservices"
	"foinlpservice/types"
	"io/ioutil"
	"net/http"
)

func eventHandler(w http.ResponseWriter, r *http.Request) {
	// Read request body
	body, err := ioutil.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Unable to read request", http.StatusBadRequest)
		return
	}
	defer r.Body.Close()

	// Parse JSON
	var events []types.EventGridEvent
	err = json.Unmarshal(body, &events)
	if err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	// Handle validation event
	if len(events) > 0 && events[0].EventType == "Microsoft.EventGrid.SubscriptionValidationEvent" {
		var validationData types.ValidationEvent
		err := json.Unmarshal(events[0].Data, &validationData)
		if err != nil {
			http.Error(w, "Invalid validation event", http.StatusBadRequest)
			return
		}

		// Respond with the validation code
		response := map[string]string{"validationResponse": validationData.ValidationCode}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(response)

		// Log that validation was successful
		fmt.Println("✅ Successfully validated Event Grid subscription")
		return
	}

	// Log received events
	for _, event := range events {
		fmt.Printf("Received Event: %+v\n", event)
		if event.EventType == "PIIEventType" {
			fmt.Printf("Processing Order ID: %s\n", string(event.Data))
			var documentData types.AzureEventGridMessage
			err = json.Unmarshal(event.Data, &documentData)
			if err != nil {
				http.Error(w, "Invalid NLP event", http.StatusBadRequest)
				return
			}
			azureservices.IdentifyPII(documentData)
		}

	}

	// Send response
	w.WriteHeader(http.StatusOK)
	fmt.Fprintln(w, "Event received")

}

func main() {
	port := "8080"
	http.HandleFunc("/", eventHandler)
	fmt.Println("Event Grid subscriber listening on port 8080...")
	err := http.ListenAndServe(":"+port, nil)
	if err != nil {
		fmt.Println("❌ Error starting server:", err)
	}
}
