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

func main() {

	start := time.Now()

	logfilepath := utils.ViperEnvVariable("logfilepath")
	file, err := os.OpenFile(logfilepath+start.Format("2006-01-02")+"nlplog.txt", os.O_WRONLY|os.O_CREATE|os.O_APPEND, 0644)

	if err != nil {
		fmt.Println("Error opening file:", err)
		return
	}
	defer file.Close()

	// Redirect stdout to the file.
	os.Stdout = file

	fmt.Println("Start Time :" + start.String())

	timeoutCounter := 0
	maxTimeouts, err := strconv.Atoi(utils.ViperEnvVariable("eventgridmaxtimeouts"))
	if err != nil {
		log.Printf("Error getting maxtimeouts env %v", err)
	}
	timeoutDuration, err := strconv.Atoi(utils.ViperEnvVariable("eventgridtimeoutseconds"))
	if err != nil {
		log.Printf("Error getting eventgridtimeoutseconds env %v", err)
	}
	eventgridendpoint := utils.ViperEnvVariable("eventgridendpoint")
	eventgridapiversion := utils.ViperEnvVariable("eventgridapiversion")
	eventgridaccesskey := utils.ViperEnvVariable("eventgridaccesskey")
	eventgridmaxevents := utils.ViperEnvVariable("eventgridmaxevents")
	maxEvents, err := strconv.Atoi(eventgridmaxevents)
	if err != nil {
		log.Printf("Error getting maxevents env %v", err)
	}
	successCount := 0

	dequeueditems := 0

	for dequeueditems < 995 { // azure PII has limit of 1000 api calls / min

		dequeueditems += maxEvents

		req, err := http.NewRequest("POST", eventgridendpoint+"receive?"+eventgridapiversion+"&maxEvents="+eventgridmaxevents, nil)
		if err != nil {
			log.Printf("Failed to create request: %v", err)
			bufio.NewReader(os.Stdin).ReadBytes('\n')
			log.Printf("Failed to create request: %v", err)
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
			// log.Printf("Failed to send request: %v", err)
		}

		// Parse the response body
		body, err := io.ReadAll(resp.Body)
		// fmt.Println("body:", body)
		if err != nil {
			log.Printf("failed to read response body: %v", err)
			bufio.NewReader(os.Stdin).ReadBytes('\n')
			log.Printf("failed to read response body: %v", err)
			// return nil, fmt.Errorf("failed to read response body: %w", err)
		}
		// fmt.Printf("Response Body: %s\n", string(body))

		var eventResponse types.EventGridResponse
		err = json.Unmarshal(body, &eventResponse)
		if err != nil {
			log.Printf("Invalid JSON: %v", err)
			bufio.NewReader(os.Stdin).ReadBytes('\n')
			log.Printf("Invalid JSON: %v", err)
			// return
		}

		var wg sync.WaitGroup
		var lockTokens []string
		var eventInfo []string
		// const maxConcurrency = 200
		sem := make(chan struct{}, maxEvents)

		var payloads []types.SolrPayload

		results := make(chan types.SolrPayload, maxEvents)

		// log.Println(len(eventResponse.Value))

		for _, event := range eventResponse.Value {
			lockToken := event.BrokerProperties.LockToken
			lockTokens = append(lockTokens, lockToken)
			eventInfo = append(eventInfo, event.Event.Data.FoiDocumentFilename+" page "+strconv.Itoa(event.Event.Data.FoiDocumentPageNumber))

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
		log.Printf("payloads: %v", payloads)

		solrsearchservices.SaveDocumentPIIToSolr(payloads)

		acknowledgePayload := types.AcknowledgePayload{
			LockTokens: lockTokens,
		}

		payloadBytes, err := json.Marshal(acknowledgePayload)
		req, err = http.NewRequest("POST", eventgridendpoint+"acknowledge?"+eventgridapiversion, bytes.NewBuffer(payloadBytes))
		if err != nil {
			log.Printf("Failed to create request: %v", err)
			bufio.NewReader(os.Stdin).ReadBytes('\n')
			log.Printf("Failed to create request: %v", err)
		}

		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("Authorization", "SharedAccessKey "+eventgridaccesskey)

		client = &http.Client{Timeout: 5 * time.Second}
		resp, err = client.Do(req)
		if err != nil {
			log.Printf("Failed to send ack request: %v", err)
			bufio.NewReader(os.Stdin).ReadBytes('\n')
			log.Printf("Failed to send ack request: %v", err)
		}
		fmt.Printf("HTTP Status Code: %d\n", resp.StatusCode)
		// Handle non-200 HTTP responses
		if resp.StatusCode != http.StatusOK {
			log.Printf("unexpected response status: %s", resp.Status)
			bufio.NewReader(os.Stdin).ReadBytes('\n')
			log.Printf("unexpected response status: %s", resp.Status)
		}
		body, err = io.ReadAll(resp.Body)
		fmt.Printf("Response Body: %s\n", string(body))

		defer resp.Body.Close()
		var acknowledgeResponse types.AcknowledgeResponse
		err = json.Unmarshal(body, &acknowledgeResponse)

		if len(acknowledgeResponse.SucceededLockTokens) > 0 {
			successCount += len(acknowledgeResponse.SucceededLockTokens)
		}

		for _, event := range eventInfo {
			fmt.Println(event)
		}

	}

	fmt.Println("Successfully Dequeued:", successCount)

	end := time.Now()
	fmt.Println("End Time :" + end.String())
	total := end.Sub(start)
	fmt.Println("Total time:" + total.String())
}
