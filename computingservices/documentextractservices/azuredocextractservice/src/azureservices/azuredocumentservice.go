package azureservices

import (
	"azuredocextractservice/types"
	"azuredocextractservice/utils"
	"fmt"
)

func CallAzureDocument(jsonPayload []byte, document types.Documents, request types.Requests) (types.AnalyzeResults, error) {
	subscriptionKey := utils.ViperEnvVariable("azuresubcriptionkey")
	baseURL := utils.ViperEnvVariable("azuredocumentaiendpoint")

	service := NewAzureService(subscriptionKey, baseURL)

	result, err := service.AnalyzeAndExtractDocument(jsonPayload, document, request)
	if err != nil {
		fmt.Printf("Error calling Azure Document API: %v\n", err)
	}

	return result, err
}
