package types

import "time"

type SOLRSearchDocument struct {
	Foisolrid              string    `json:"id"`
	FoiDocumentID          string    `json:"foidocumentid"`
	FoiRequestNumber       string    `json:"foirequestnumber"`
	FoiMinistryRequestID   string    `json:"foiministryrequestid"`
	FoiMinistryCode        string    `json:"foiministrycode"`
	FoiDocumentFileName    string    `json:"foidocumentfilename"`
	FoiDocumentPageNumber  int       `json:"foidocumentpagenumber"`
	FoiDocumentSentence    string    `json:"foidocumentsentence"`
	FoiDocumentSentenceID  int       `json:"foidocumentsentenceId"`
	FoiRequestReceivedDate time.Time `json:"foirequestreceiveddate"`
	FoiDocumentURL         string    `json:"foidocumenturl"`
	FoiRequestpublicbody   string    `json:"foirequestpublicbody"`
	FoiRequestType         string    `json:"foirequesttype"`
	FoiRequestMiscInfo     string    `json:"foirequestmiscinfo"`
}
