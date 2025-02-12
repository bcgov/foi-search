@description('Array of Private Endpoint configurations')
param peConfig object

@description('The location for all Private Endpoints')
param location string

resource privateEndpoints 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: peConfig.name
  location: location
  tags: peConfig.tags
  properties: {
    privateLinkServiceConnections: [
      {
        name: peConfig.name
        properties: {
          privateLinkServiceId: peConfig.privateLinkServiceId
          groupIds: peConfig.groupIds
        }
      }
    ]
    customNetworkInterfaceName: peConfig.customNetworkInterfaceName
    subnet: {
      id: peConfig.subnetId
    }
    applicationSecurityGroups: peConfig.applicationSecurityGroups
  }
}

