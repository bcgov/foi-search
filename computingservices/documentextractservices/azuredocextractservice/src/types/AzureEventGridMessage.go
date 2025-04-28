package types

type AzureEventGridMessage struct {
	Foisolrid             string `json:"id"`
	FoiDocumentID         string `json:"foidocumentid"`
	FoiRequestNumber      string `json:"foirequestnumber"`
	FoiMinistryRequestID  string `json:"foiministryrequestid"`
	FoiDocumentPageNumber int    `json:"foidocumentpagenumber"`
	FoiDocumentURL        string `json:"foidocumenturl"`
	Content               string `json:"content"`
}

// EventGridEvent represents the structure of an event in Event Grid.
type EventGridEvent struct {
	ID        string                `json:"id"`
	Subject   string                `json:"subject"`
	Data      AzureEventGridMessage `json:"data"`
	EventType string                `json:"eventType"`
	Time      string                `json:"eventTime"`
}

type CloudEvent struct {
	ID              string                `json:"id"`
	Source          string                `json:"source"`
	Subject         string                `json:"subject"`
	SpecVersion     string                `json:"specversion"`
	Data            AzureEventGridMessage `json:"data"`
	DataContentType string                `json:"datacontenttype"`
	Type            string                `json:"type"`
	Time            string                `json:"time"`
}
