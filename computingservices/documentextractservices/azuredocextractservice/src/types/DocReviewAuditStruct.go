package types

type DocReviewAudit struct {
	ExtractionJobId   int    `json:"extractionjobid`
	Version           int    `json:"version"`
	DocumentID        int64  `json:"documentid"`
	MinistryRequestID int64  `json:"ministryrequestid"`
	Status            string `json:"status"`
	Description       string `json:"message"`
}
