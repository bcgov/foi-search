package amqpservices

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"time"

	"azuredocextractservice/types"

	"github.com/Azure/go-amqp"
)

// Message struct to map the JSON structure

// ProcessMessage connects to the broker and processes messages from the queue
func ProcessMessage() ([]types.QueueMessage, error) {
	brokerURL := "amqp://admin:admin@localhost:5672" // Replace with your broker URL
	queueName := "documents"                         // Replace with your queue name

	conn, err := connectToBroker(brokerURL)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to broker: %w", err)
	}
	defer closeConnection(conn)

	session, err := createSession(conn)
	if err != nil {
		return nil, fmt.Errorf("failed to create session: %w", err)
	}

	receiver, err := createReceiver(session, queueName)
	if err != nil {
		return nil, fmt.Errorf("failed to create receiver: %w", err)
	}
	defer receiver.Close(context.Background())

	fmt.Printf("Listening for messages on queue: %s\n", queueName)
	return processQueue(receiver)
}

// connectToBroker establishes a connection to the AMQP broker
func connectToBroker(brokerURL string) (*amqp.Conn, error) {
	ctx := context.Background()
	conn, err := amqp.Dial(ctx, brokerURL, nil)
	if err != nil {
		return nil, err
	}
	fmt.Println("Connected to the broker")
	return conn, nil
}

// closeConnection ensures the AMQP connection is properly closed
func closeConnection(conn *amqp.Conn) {
	fmt.Println("Closing connection to the broker...")
	conn.Close()
	fmt.Println("Connection closed.")
}

// createSession creates a new AMQP session
func createSession(conn *amqp.Conn) (*amqp.Session, error) {
	session, err := conn.NewSession(context.Background(), nil)
	if err != nil {
		return nil, err
	}
	return session, nil
}

// createReceiver initializes a receiver for the specified queue
func createReceiver(session *amqp.Session, queueName string) (*amqp.Receiver, error) {
	receiver, err := session.NewReceiver(context.Background(),
		queueName,
		&amqp.ReceiverOptions{Credit: 10}) // Prefetch 10 messages
	if err != nil {
		return nil, err
	}
	return receiver, nil
}

// processQueue handles the messages from the queue
func processQueue(receiver *amqp.Receiver) ([]types.QueueMessage, error) {
	var messages []types.QueueMessage
	timeoutCounter := 0
	maxTimeouts := 1

	for {
		ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()

		msg, err := receiveMessage(receiver, ctx)
		if errors.Is(err, context.DeadlineExceeded) {
			timeoutCounter++
			fmt.Printf("No messages received within the timeout (%d/%d)\n", timeoutCounter, maxTimeouts)

			if timeoutCounter >= maxTimeouts {
				fmt.Println("No more messages in the queue. Exiting...")
				break
			}
			continue
		} else if err != nil {
			return nil, fmt.Errorf("error receiving message: %w", err)
		}

		timeoutCounter = 0
		message, err := processMessageContent(msg)
		if err != nil {
			log.Printf("Failed to process message: %v", err)
			continue
		}

		if err := acknowledgeMessage(receiver, ctx, msg); err != nil {
			log.Printf("Failed to acknowledge message: %v", err)
		}

		messages = append(messages, message)
	}

	fmt.Println("All messages processed. Exiting.")
	return messages, nil
}

// receiveMessage handles receiving a message from the queue
func receiveMessage(receiver *amqp.Receiver, ctx context.Context) (*amqp.Message, error) {
	msg, err := receiver.Receive(ctx, nil)
	if err != nil {
		return nil, err
	}
	return msg, nil
}

// processMessageContent processes the content of the received message
func processMessageContent(msg *amqp.Message) (types.QueueMessage, error) {
	rawData := msg.Value
	rawDataBytes, err := convertToBytes(rawData)
	if err != nil {
		return types.QueueMessage{}, fmt.Errorf("failed to convert message data: %w", err)
	}

	var message types.QueueMessage
	if err := json.Unmarshal(rawDataBytes, &message); err != nil {
		return types.QueueMessage{}, fmt.Errorf("failed to unmarshal message: %w", err)
	}

	fmt.Printf("Extracted s3uri: %s\n", message.S3Uri)
	return message, nil
}

// convertToBytes converts the raw data to a byte slice
func convertToBytes(rawData interface{}) ([]byte, error) {
	switch v := rawData.(type) {
	case []byte:
		return v, nil
	case string:
		return []byte(v), nil
	default:
		return nil, errors.New("unsupported data type")
	}
}

// acknowledgeMessage acknowledges the processed message
func acknowledgeMessage(receiver *amqp.Receiver, ctx context.Context, msg *amqp.Message) error {
	return receiver.AcceptMessage(ctx, msg)
}
