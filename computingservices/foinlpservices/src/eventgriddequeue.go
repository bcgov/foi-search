package main

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"foinlpservice/azureservices"
	"foinlpservice/solrsearchservices"
	"foinlpservice/types"
	"foinlpservice/utils"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"
	"sync"
	"time"
)

// func eventHandler(w http.ResponseWriter, r *http.Request) {
// 	// Read request body
// 	body, err := ioutil.ReadAll(r.Body)
// 	if err != nil {
// 		http.Error(w, "Unable to read request", http.StatusBadRequest)
// 		return
// 	}
// 	defer r.Body.Close()

// 	// Parse JSON
// 	var events []types.EventGridEvent
// 	err = json.Unmarshal(body, &events)
// 	if err != nil {
// 		http.Error(w, "Invalid JSON", http.StatusBadRequest)
// 		return
// 	}

// 	// Handle validation event
// 	if len(events) > 0 && events[0].EventType == "Microsoft.EventGrid.SubscriptionValidationEvent" {
// 		var validationData types.ValidationEvent
// 		err := json.Unmarshal(events[0].Data, &validationData)
// 		if err != nil {
// 			http.Error(w, "Invalid validation event", http.StatusBadRequest)
// 			return
// 		}

// 		// Respond with the validation code
// 		response := map[string]string{"validationResponse": validationData.ValidationCode}
// 		w.Header().Set("Content-Type", "application/json")
// 		json.NewEncoder(w).Encode(response)

// 		// Log that validation was successful
// 		fmt.Println("✅ Successfully validated Event Grid subscription")
// 		return
// 	}

// 	// Log received events
// 	for _, event := range events {
// 		fmt.Printf("Received Event: %+v\n", event)
// 		if event.EventType == "PIIEventType" {
// 			fmt.Printf("Processing Order ID: %s\n", string(event.Data))
// 			var documentData types.AzureEventGridMessage
// 			err = json.Unmarshal(event.Data, &documentData)
// 			if err != nil {
// 				http.Error(w, "Invalid NLP event", http.StatusBadRequest)
// 				return
// 			}
// 			azureservices.IdentifyPII(documentData)
// 		}

// 	}

// 	// Send response
// 	w.WriteHeader(http.StatusOK)
// 	fmt.Fprintln(w, "Event received")

// }

func main() {
	// port := "8080"
	// http.HandleFunc("/", eventHandler)
	// fmt.Println("Event Grid subscriber listening on port 8080...")
	// err := http.ListenAndServe(":"+port, nil)
	// if err != nil {
	// 	fmt.Println("❌ Error starting server:", err)
	// }

	start := time.Now()
	fmt.Println("Start Time :" + start.String())

	timeoutCounter := 0
	maxTimeouts, err := strconv.Atoi(utils.ViperEnvVariable("eventgridmaxtimeouts"))
	if err != nil {
		log.Fatalf("Error getting maxtimeouts env %v", err)
	}
	timeoutDuration, err := strconv.Atoi(utils.ViperEnvVariable("eventgridtimeoutseconds"))
	if err != nil {
		log.Fatalf("Error getting eventgridtimeoutseconds env %v", err)
	}
	eventgridendpoint := utils.ViperEnvVariable("eventgridendpoint")
	eventgridapiversion := utils.ViperEnvVariable("eventgridapiversion")
	eventgridaccesskey := utils.ViperEnvVariable("eventgridaccesskey")
	eventgridmaxevents := utils.ViperEnvVariable("eventgridmaxevents")
	maxEvents, err := strconv.Atoi(eventgridmaxevents)
	if err != nil {
		log.Fatalf("Error getting maxevents env %v", err)
	}
	successCount := 0

	dequeueditems := 0

	for dequeueditems < 995 { // azure PII has limit of 1000 api calls / min

		dequeueditems += maxEvents

		req, err := http.NewRequest("POST", eventgridendpoint+"receive?"+eventgridapiversion+"&maxEvents="+eventgridmaxevents, nil)
		if err != nil {
			log.Printf("Failed to create request: %v", err)
			bufio.NewReader(os.Stdin).ReadBytes('\n')
			log.Fatalf("Failed to create request: %v", err)
		}

		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("Authorization", "SharedAccessKey "+eventgridaccesskey)

		client := &http.Client{Timeout: time.Duration(timeoutDuration) * time.Second}
		resp, err := client.Do(req)
		if err != nil {
			err2 := fmt.Errorf("error making HTTP request: %w", err)
			if errors.Is(err2, context.DeadlineExceeded) {
				timeoutCounter++
				fmt.Println(err2.Error())
				if timeoutCounter >= maxTimeouts {
					fmt.Println("No more messages in the queue. Exiting...")
					break
				}
				continue
			}
			// log.Fatalf("Failed to send request: %v", err)
		}

		// Parse the response body
		body, err := io.ReadAll(resp.Body)
		// fmt.Println("body:", body)
		if err != nil {
			log.Printf("failed to read response body: %v", err)
			bufio.NewReader(os.Stdin).ReadBytes('\n')
			log.Fatalf("failed to read response body: %v", err)
			// return nil, fmt.Errorf("failed to read response body: %w", err)
		}
		// fmt.Printf("Response Body: %s\n", string(body))

		var eventResponse types.EventGridResponse
		err = json.Unmarshal(body, &eventResponse)
		if err != nil {
			log.Printf("Invalid JSON: %v", err)
			bufio.NewReader(os.Stdin).ReadBytes('\n')
			log.Fatalf("Invalid JSON: %v", err)
			// return
		}

		var wg sync.WaitGroup
		var lockTokens []string
		// const maxConcurrency = 200
		sem := make(chan struct{}, maxEvents)

		var payloads []types.SolrPayload

		results := make(chan types.SolrPayload, maxEvents)

		log.Println(len(eventResponse.Value))

		for _, event := range eventResponse.Value {
			lockToken := event.BrokerProperties.LockToken
			lockTokens = append(lockTokens, lockToken)

			wg.Add(1)
			sem <- struct{}{}

			go func(event types.Message) {
				data := event.Event.Data
				// document := solrsearchservices.GetSolrDocumentByID(data.Foisolrid)
				pii := azureservices.IdentifyPII(data.Content, client)
				// fmt.Println(data.Foisolrid)
				results <- types.SolrPayload{
					ID: data.Foisolrid,
					FoipiiJSON: types.FoipiiJSON{
						Set: []string{pii},
					},
				}
				<-sem
				wg.Done()
			}(event)

			// fmt.Println("lockToken:", lockToken)

		}
		wg.Wait()
		close(results)

		for res := range results {
			payloads = append(payloads, res)
		}

		solrsearchservices.SaveDocumentPIIToSolr(payloads)

		acknowledgePayload := types.AcknowledgePayload{
			LockTokens: lockTokens,
		}

		payloadBytes, err := json.Marshal(acknowledgePayload)
		req, err = http.NewRequest("POST", eventgridendpoint+"acknowledge?"+eventgridapiversion, bytes.NewBuffer(payloadBytes))
		if err != nil {
			log.Printf("Failed to create request: %v", err)
			bufio.NewReader(os.Stdin).ReadBytes('\n')
			log.Fatalf("Failed to create request: %v", err)
		}

		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("Authorization", "SharedAccessKey "+eventgridaccesskey)

		client = &http.Client{Timeout: 5 * time.Second}
		resp, err = client.Do(req)
		if err != nil {
			log.Printf("Failed to send ack request: %v", err)
			bufio.NewReader(os.Stdin).ReadBytes('\n')
			log.Fatalf("Failed to send ack request: %v", err)
		}
		fmt.Printf("HTTP Status Code: %d\n", resp.StatusCode)
		// Handle non-200 HTTP responses
		if resp.StatusCode != http.StatusOK {
			log.Printf("unexpected response status: %s", resp.Status)
			bufio.NewReader(os.Stdin).ReadBytes('\n')
			log.Fatalf("unexpected response status: %s", resp.Status)
		}
		body, err = io.ReadAll(resp.Body)
		fmt.Printf("Response Body: %s\n", string(body))

		defer resp.Body.Close()
		var acknowledgeResponse types.AcknowledgeResponse
		err = json.Unmarshal(body, &acknowledgeResponse)
		// if len(acknowledgeResponse.FailedLockTokens) > 0 {
		// 	// timeoutCounter++
		// 	// if timeoutCounter >= maxTimeouts {
		// 	fmt.Println("Failed Token: " + acknowledgeResponse.FailedLockTokens)
		// 		// break
		// 	// }
		// } else

		if len(acknowledgeResponse.SucceededLockTokens) > 0 {
			successCount += len(acknowledgeResponse.SucceededLockTokens)
		}

	}

	fmt.Println("Successfully Dequeued:", successCount)

	end := time.Now()
	fmt.Println("End Time :" + end.String())
	total := end.Sub(start)
	fmt.Println("Total time:" + total.String())
}
