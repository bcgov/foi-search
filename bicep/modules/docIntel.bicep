// Parameter for the name of the Cognitive Services resource
param docIntelConfig object

param docIntelName string

// Parameter for the location where the resource will be deployed
param location string

// Define the Cognitive Services resource (Form Recognizer in this case)
resource documentIntelligence 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  // The name of the resource
  name: docIntelName

  // The location where the resource will be deployed
  location: location

  // The SKU for the Cognitive Services account, which defines the pricing tier
  sku: {
    name: docIntelConfig.skuName
  }

  // The type of Cognitive Services account (Form Recognizer in this case)
  kind: docIntelConfig.kind

  // Properties of the resource
  properties: {
    // Public network access setting, this controls whether the service is publicly accessible
    publicNetworkAccess: docIntelConfig.publicNetworkAccess
  }
}
