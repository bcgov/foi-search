@description('Object of Private Endpoint configurations')
param peConfig object

@description('The location for all Private Endpoints')
param location string

@description('Array of Application Security Groups associated with the Private Endpoint')
param applicationSecurityGroups array

@description('The Subnet ID where the Private Endpoint will be deployed')
param subnetId string

@description('The Private Link Service ID for the target resource')
param privateLinkServiceId string

// Deploy a Private Endpoint to securely connect to an Azure service
resource privateEndpoints 'Microsoft.Network/privateEndpoints@2024-05-01' = {
  name: peConfig.name
  location: location
  properties: {
    privateLinkServiceConnections: [
      {
        name: peConfig.name
        properties: {
          // The ID of the target Private Link Service
          privateLinkServiceId: privateLinkServiceId

          // The specific group of the service to connect to
          groupIds: peConfig.groupIds
        }
      }
    ]
    
    // Custom name for the associated network interface
    customNetworkInterfaceName: peConfig.customNetworkInterfaceName

    // Subnet where the Private Endpoint will be deployed
    subnet: {
      id: subnetId
    }

    // Optional: Attach Application Security Groups if provided
    applicationSecurityGroups: applicationSecurityGroups
  }
}
