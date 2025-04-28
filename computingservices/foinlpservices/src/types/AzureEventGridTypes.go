package types

import "encoding/json"

type EventGridEvent struct {
	ID        string          `json:"id"`
	Subject   string          `json:"subject"`
	EventType string          `json:"eventType"`
	EventTime string          `json:"eventTime"`
	Data      json.RawMessage `json:"data"`
}

type AzureEventGridMessage struct {
	Foisolrid             string `json:"id"`
	FoiDocumentID         string `json:"foidocumentid"`
	FoiRequestNumber      string `json:"foirequestnumber"`
	FoiMinistryRequestID  string `json:"foiministryrequestid"`
	FoiDocumentPageNumber int    `json:"foidocumentpagenumber"`
	FoiDocumentURL        string `json:"foidocumenturl"`
	Content               string `json:"content"`
}

type ValidationEvent struct {
	ValidationCode string `json:"validationCode"`
}

type EventGridResponse struct {
	Value []Message `json:"value"`
}

type Message struct {
	BrokerProperties BrokerProperties `json:"brokerProperties"`
	Event            Event            `json:"event"`
}

type BrokerProperties struct {
	LockToken     string `json:"lockToken"`
	DeliveryCount int    `json:"deliveryCount"`
}

type Event struct {
	SpecVersion     string                `json:"specversion"`
	Type            string                `json:"type"`
	Source          string                `json:"source"`
	Subject         string                `json:"subject"`
	ID              string                `json:"id"`
	Time            string                `json:"time"`
	DataContentType string                `json:"datacontenttype"`
	Data            AzureEventGridMessage `json:"data"` // If `data` can be a more complex object, use `json.RawMessage` instead
}

type AcknowledgePayload struct {
	LockTokens []string `json:"lockTokens"`
}

type AcknowledgeResponse struct {
	SucceededLockTokens []string `json:"succeededLockTokens"`
	FailedLockTokens    []string `json:"failedLockTokens"`
}
