package types

import "encoding/json"

type SolrResp struct {
	Body json.RawMessage `json:"response"`
}

type SolrRespDetails struct {
	NumFound      int            `json:"numFound"`
	Start         int            `json:"start"`
	NumFoundExact bool           `json:"numFoundExact"`
	Documents     []SolrDocument `json:"docs"`
}

type SolrDocument struct {
	ID   string   `json:"id"`
	Text []string `json:"foidocumentsentence"`
}

type FoipiiJSON struct {
	Set []string `json:"set"`
}

type SolrPayload struct {
	ID         string     `json:"id"`
	FoipiiJSON FoipiiJSON `json:"foipiijson"`
}
