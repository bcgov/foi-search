package solrsearchservices

import (
	"encoding/json"
	"fmt"
	"foinlpservice/types"
	"log"
	"net/http"
)

func GetSolrDocumentByID(id string) types.SolrDocument {
	req, err := http.NewRequest("GET", "https://solr-fc7a67-dev.apps.gold.devops.gov.bc.ca/solr/foisearch/get?ids="+id, nil)
	if err != nil {
		log.Fatalf("Failed to create request: %v", err)
	}

	req.Header.Set("Authorization", "Basic YWRtaW46Rm9pMTIz")

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

	fmt.Printf("Response: %s\n", string(solrresponse.Body))

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
