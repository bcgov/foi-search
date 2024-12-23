package azureservices

import (
	"azuredocextractservice/utils"
	"log"
)

func CallAzureDocument(jsonPayload []byte) (map[string]interface{}, error) {
	subscriptionKey := utils.ViperEnvVariable("azuresubcriptionkey")
	baseURL := "https://foidocintelservice.cognitiveservices.azure.com"

	service := NewAzureService(subscriptionKey, baseURL)

	result, err := service.AnalyzeAndExtractDocument(jsonPayload)
	if err != nil {
		log.Fatalf("Error calling Azure Document API: %v", err)
	}

	return result, err
}
