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
}

type ValidationEvent struct {
	ValidationCode string `json:"validationCode"`
}