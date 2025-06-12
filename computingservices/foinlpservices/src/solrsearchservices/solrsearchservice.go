package solrsearchservices

import (
	"bytes"
	"encoding/json"
	"fmt"
	"foinlpservice/types"
	"foinlpservice/utils"
	"log"
	"net/http"
)

func GetSolrDocumentByID(id string) types.SolrDocument {
	solrendpoint := utils.ViperEnvVariable("solrendpoint")
	// fmt.Println(id)
	req, err := http.NewRequest("GET", solrendpoint+"get?ids="+id, nil)
	if err != nil {
		log.Fatalf("Failed to create request: %v", err)
	}

	req.Header.Set("Authorization", "Basic "+utils.ViperEnvVariable("solrauthkey"))

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		log.Fatalf("Failed to send request: %v", err)
	}
	defer resp.Body.Close()

	// Check the response status code
	if resp.StatusCode != http.StatusOK {
		log.Fatalf("Request failed with status code: %d", resp.StatusCode)
	}

	// var result ResponsePayload
	// if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
	// 	log.Fatalf("Failed to decode response: %v", err)
	// }
	var solrresponse types.SolrResp

	if err := json.NewDecoder(resp.Body).Decode(&solrresponse); err != nil {
		log.Fatalf("Failed to decode response: %v", err)
	}

	// fmt.Printf("Response: %s\n", string(solrresponse.Body))

	var solrdetails types.SolrRespDetails

	err = json.Unmarshal(solrresponse.Body, &solrdetails)

	if !solrdetails.NumFoundExact {
		log.Fatalf("More than one solr result returned")
	}

	if solrdetails.Documents[0].ID != id {
		log.Fatalf("Incorrect ID returned: %v", err)
	}

	return solrdetails.Documents[0]
}

func SaveDocumentPIIToSolr(payload []types.SolrPayload) bool {

	// fmt.Println(id)

	// Convert the struct to JSON
	// jsonData, err := json.Marshal(searchdocs)
	// fmt.Println("SOLR Search Data starts here")
	// fmt.Println(string(jsonData))
	// fmt.Println("SOLR Search Data ends here")
	// if err != nil {
	// 	log.Fatal("Error marshaling JSON:", err)
	// }

	// payload := []types.SolrPayload{
	// 	{
	// 		ID: id,
	// 		FoipiiJSON: types.FoipiiJSON{
	// 			Set: []string{pii},
	// 		},
	// 	},
	// }

	// Convert to JSON
	jsonBytes, err := json.Marshal(payload)
	if err != nil {
		panic(err)
	}

	fmt.Println(string(jsonBytes))

	// Solr endpoint URL (Replace with your Solr endpoint)
	url := utils.ViperEnvVariable("solrendpoint")
	// Create a POST request with JSON data
	// fmt.Println(url + "update?commit=true")
	req, err := http.NewRequest("POST", url+"update?commit=true", bytes.NewBuffer(jsonBytes))
	if err != nil {
		log.Fatal("Error creating request:", err)
	}

	// Set the appropriate headers for JSON content
	req.Header.Set("Content-Type", "application/json")
	username := utils.ViperEnvVariable("solradmin")
	password := utils.ViperEnvVariable("solrpassword")
	req.SetBasicAuth(username, password)
	// Send the request using the http client
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		log.Fatal("Error sending request:", err)
	} else {
		fmt.Printf("Response Status: %s\n", resp.Status)
	}
	defer resp.Body.Close()

	// Handle the response
	if resp.StatusCode == http.StatusOK {
		fmt.Println("Successfully posted to Solr")
		return true
	} else {
		fmt.Printf("Failed to post to Solr. Status: %s\n", resp.Status)
		return false
	}

}
