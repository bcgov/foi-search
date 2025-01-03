package types

type Divisions struct {
	DivisionID int64  `json:"DivisionID"`
	Name       string `json:"Name"`
}

type Documents struct {
	DocumentID    int64       `json:"DocumentID"`
	DocumentName  string      `json:"DocumentName"`
	DocumentType  string      `json:"DocumentType"`
	CreatedDate   string      `json:"CreatedDate"`
	DocumentS3URL string      `json:"DocumentS3URL"`
	Divisions     []Divisions `json:"Documents"`
}

type Requests struct {
	MinistryRequestID string      `json:"MinistryRequestID"`
	RequestNumber     string      `json:"RequestNumber"`
	RequestType       string      `json:"RequestType"`
	MinistryCode      string      `json:"MinistryCode"`
	ReceivedDate      string      `json:"ReceivedDate"`
	RequestMiscInfo   string      `json:"RequestMiscInfo"`
	Documents         []Documents `json:"Documents"`
}

type QueueMessage struct {
	BatchID  string     `json:"BatchID"`
	Date     string     `json:"Date"`
	Requests []Requests `json:"Requests"`
}
