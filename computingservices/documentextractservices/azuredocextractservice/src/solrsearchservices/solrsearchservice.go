package solrsearchservices

import (
	"azuredocextractservice/types"
	"azuredocextractservice/utils"
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
)

func PushtoSolr(searchdocs []types.SOLRSearchDocument) bool {

	// Convert the struct to JSON
	jsonData, err := json.Marshal(searchdocs)
	// fmt.Println("SOLR Search Data starts here")
	// fmt.Println(string(jsonData))
	// fmt.Println("SOLR Search Data ends here")
	if err != nil {
		log.Fatal("Error marshaling JSON:", err)
	}

	// Solr endpoint URL (Replace with your Solr endpoint)
	url := utils.ViperEnvVariable("foisearchsolrpostendpoint")
	// Create a POST request with JSON data
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
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
