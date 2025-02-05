package types

type AzureEventGridMessage struct {
	Foisolrid             string `json:"id"`
	FoiDocumentID         string `json:"foidocumentid"`
	FoiRequestNumber      string `json:"foirequestnumber"`
	FoiMinistryRequestID  string `json:"foiministryrequestid"`
	FoiDocumentPageNumber int    `json:"foidocumentpagenumber"`
	FoiDocumentURL        string `json:"foidocumenturl"`
}
