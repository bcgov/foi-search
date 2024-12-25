package types

type SOLRSearchDocument struct {
	FoiDocumentID         string `json:"foidocumentid"`
	FoiRequestNumber      string `json:"foirequestnumber"`
	FoiMinistryRequestID  string `json:"foiministryrequestid"`
	FoiMinistryCode       string `json:"foiministrycode"`
	FoiDocumentFileName   string `json:"foidocumentfilename"`
	FoiDocumentPageNumber int    `json:"foidocumentpagenumber"`
	FoiDocumentSentence   string `json:"foidocumentsentence"`
	FoiDocumentSentenceID int    `json:"foidocumentsentenceId"`
	FoiRequestMiscInfo    string `json:"foirequestmiscinfo"`
}
