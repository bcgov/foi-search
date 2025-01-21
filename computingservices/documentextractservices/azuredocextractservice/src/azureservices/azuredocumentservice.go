package azureservices

import (
	"azuredocextractservice/types"
	"azuredocextractservice/utils"
	"log"
)

func CallAzureDocument(jsonPayload []byte, document types.Documents, request types.Requests) (types.AnalyzeResults, error) {
	subscriptionKey := utils.ViperEnvVariable("azuresubcriptionkey")
	baseURL := "https://foidocintelservice.cognitiveservices.azure.com"

	service := NewAzureService(subscriptionKey, baseURL)

	result, err := service.AnalyzeAndExtractDocument(jsonPayload, document, request)
	if err != nil {
		log.Fatalf("Error calling Azure Document API: %v", err)
	}

	return result, err
}
