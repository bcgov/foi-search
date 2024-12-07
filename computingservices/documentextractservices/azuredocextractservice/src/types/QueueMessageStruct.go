package types

type QueueMessage struct {
	S3Uri             string `json:"s3Uri"`
	MinistryRequestId int64  `json:"ministryRequestId"`
	RequestNumber     string `json:"requestNumber"`
	MinistryCode      string `json:"ministryCode"`
	DivisionName      string `json:"divisionName"`
	ModifiedDate      string `json:"modifiedDate"`
	DocumentHashCode  string `json:"documentHashCode"`
}
