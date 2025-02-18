// Parameter for the name of the Cognitive Services resource
param docIntel object

// Parameter for the location where the resource will be deployed
param location string



// Define the Cognitive Services resource (Form Recognizer in this case)
resource documentIntelligence 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  // The name of the resource
  name: docIntel.name

  // The location where the resource will be deployed
  location: location

  // The SKU for the Cognitive Services account, which defines the pricing tier
  sku: {
    name: docIntel.skuName
  }

  // The type of Cognitive Services account (Form Recognizer in this case)
  kind: 'FormRecognizer'

  // Identity configuration for the resource (None means no managed identity)
  identity: {
    type: 'None'
  }

  // Properties of the resource
  properties: {
    // Custom subdomain name for the service, typically used to create a unique URL
    customSubDomainName: docIntel.name

    // Network ACLs to define access restrictions, default action is 'Allow'
    networkAcls: {
      defaultAction: 'Allow'
    }

    // Public network access setting, this controls whether the service is publicly accessible
    publicNetworkAccess: docIntel.publicNetworkAccess
  }
}
