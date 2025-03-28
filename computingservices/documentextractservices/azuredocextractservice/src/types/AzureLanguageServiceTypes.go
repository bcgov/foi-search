package types

// RequestPayload defines the structure of the JSON payload for the API request
type RequestPayload struct {
	Documents []Document `json:"documents"`
}

// Document represents a single document to be analyzed
type Document struct {
	ID       string `json:"id"`
	Text     string `json:"text"`
	Language string `json:"language"`
}

// ResponsePayload defines the structure of the JSON response from the API
type ResponsePayload struct {
	Documents []struct {
		ID       string      `json:"id"`
		Entities []PIIEntity `json:"entities"`
	} `json:"documents"`
	Errors []interface{} `json:"errors"`
}

// Entity represents a detected PII entity
type PIIEntity struct {
	Text            string  `json:"text"`
	Category        string  `json:"category"`
	SubCategory     string  `json:"subCategory"`
	ConfidenceScore float64 `json:"confidenceScore"`
}
