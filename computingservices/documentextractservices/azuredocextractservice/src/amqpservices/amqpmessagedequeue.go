package amqpservices

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"time"

	"azuredocextractservice/types"
)

// ActiveMQ REST API configuration
const (
	activeMQBaseURL = "http://localhost:8161/api/message" // Base URL for ActiveMQ REST API
	username        = "admin"                             // ActiveMQ admin username
	password        = "admin"                             // ActiveMQ admin password
)

// ProcessMessage fetches messages from the ActiveMQ queue using HTTP
func ProcessMessage() ([]types.QueueMessage, error) {
	queueName := "docs1" // Replace with your queue name
	// Construct the URL to fetch messages from the queue
	url := fmt.Sprintf("%s/%s?type=queue", activeMQBaseURL, queueName)

	messages := []types.QueueMessage{}
	timeoutCounter := 0
	maxTimeouts := 1

	for {
		// Make a GET request to fetch the message
		message, err := fetchMessageFromQueue(url)
		if err != nil {
			if errors.Is(err, context.DeadlineExceeded) {
				timeoutCounter++
				fmt.Printf("No messages received within the timeout (%d/%d)\n", timeoutCounter, maxTimeouts)

				if timeoutCounter >= maxTimeouts {
					fmt.Println("No more messages in the queue. Exiting...")
					break
				}
				continue
			}
			return nil, fmt.Errorf("error fetching message: %w", err)
		}

		if message == nil {
			fmt.Println("No more messages in the queue. Exiting...")
			break
		}

		// Process the received message
		fmt.Printf("Extracted s3uri: %s\n", message.S3Uri)
		messages = append(messages, *message)
	}

	fmt.Println("All messages processed. Exiting.")
	return messages, nil
}

// fetchMessageFromQueue fetches a single message from the queue
func fetchMessageFromQueue(url string) (*types.QueueMessage, error) {
	fmt.Println("URL:", url)

	client := &http.Client{Timeout: 30 * time.Second}
	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create HTTP request: %w", err)
	}

	// Add basic authentication
	req.Header.Set("Content-Type", "application/json")
	req.SetBasicAuth(username, password)
	//req.Header.Set("Authorization", "Basic " + base64.StdEncoding.EncodeToString([]byte("username:password")))

	// Make the HTTP request
	resp, err := client.Do(req)
	fmt.Println("resp:", resp)
	if err != nil {
		return nil, fmt.Errorf("error making HTTP request: %w", err)
	}
	defer resp.Body.Close()
	fmt.Printf("HTTP Status Code: %d\n", resp.StatusCode)

	// Handle non-200 HTTP responses
	if resp.StatusCode != http.StatusOK {
		if resp.StatusCode == http.StatusNoContent {
			// No messages in the queue
			return nil, nil
		}
		return nil, fmt.Errorf("unexpected response status: %s", resp.Status)
	}

	// Parse the response body
	body, err := io.ReadAll(resp.Body)
	fmt.Println("body:", body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response body: %w", err)
	}
	fmt.Printf("Response Body: %s\n", string(body))
	var message types.QueueMessage
	if err := json.Unmarshal(body, &message); err != nil {
		return nil, fmt.Errorf("failed to unmarshal message: %w", err)
	}

	return &message, nil
}
