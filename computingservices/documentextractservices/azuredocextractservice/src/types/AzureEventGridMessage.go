package types

type AzureEventGridMessage struct {
	Foisolrid             string `json:"id"`
	FoiDocumentID         string `json:"foidocumentid"`
	FoiRequestNumber      string `json:"foirequestnumber"`
	FoiMinistryRequestID  string `json:"foiministryrequestid"`
	FoiDocumentPageNumber int    `json:"foidocumentpagenumber"`
	FoiDocumentURL        string `json:"foidocumenturl"`
}

// EventGridEvent represents the structure of an event in Event Grid.
type EventGridEvent struct {
	ID        string                `json:"id"`
	Subject   string                `json:"subject"`
	Data      AzureEventGridMessage `json:"data"`
	EventType string                `json:"eventType"`
	Time      string                `json:"eventTime"`
}
