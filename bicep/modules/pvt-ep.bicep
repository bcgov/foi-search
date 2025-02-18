@description('object of Private Endpoint configurations')
param peConfig object

@description('The location for all Private Endpoints')
param location string

param applicationSecurityGroups array

param subnetId string

param privateLinkServiceId string

resource privateEndpoints 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: peConfig.name
  location: location
  properties: {
    privateLinkServiceConnections: [
      {
        name: peConfig.name
        properties: {
          privateLinkServiceId: privateLinkServiceId
          groupIds: peConfig.groupIds
        }
      }
    ]
    customNetworkInterfaceName: peConfig.customNetworkInterfaceName
    subnet: {
      id: subnetId
    }
    applicationSecurityGroups: applicationSecurityGroups
  }
}

