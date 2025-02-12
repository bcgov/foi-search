@description('The name of the virtual network')
param vnetName string

@description('Array of subnets with offset and mask')
param subnets array

param nsgMapping object

// Reference existing VNet
resource virtualNetwork 'Microsoft.Network/virtualNetworks@2024-05-01' existing = {
  name: vnetName
}

// Update the subnets array with the correct NSG ID
var updatedSubnets = [
  for subnet in subnets: {
    name: subnet.name
    offset: subnet.offset
    mask: subnet.mask
    networkSecurityGroupId: nsgMapping[subnet.networkSecurityGroup] ?? null
    serviceEndpoints: subnet.serviceEndpoints
    privateEndpointNetworkPolicies: subnet.privateEndpointNetworkPolicies
    privateLinkServiceNetworkPolicies: subnet.privateLinkServiceNetworkPolicies
  }
]

// Extract base IP from VNet's address space
// Access the first address space in the array
var addressSpace = virtualNetwork.properties.addressSpace.addressPrefixes[0]
var cidrParts = split(addressSpace, '/')
var baseIP = cidrParts[0]
var ipOctets = split(baseIP, '.')


// Add subnets
resource subnetDeployment 'Microsoft.Network/virtualNetworks/subnets@2024-05-01' = [for subnet in updatedSubnets: {
  parent: virtualNetwork
  name: subnet.name
  properties: {
            addressPrefix: '${ipOctets[0]}.${ipOctets[1]}.${ipOctets[2]}.${int(ipOctets[3]) + subnet.offset}/${subnet.mask}'
            networkSecurityGroup: {
              id: subnet.networkSecurityGroupId // Associate an NSG to the subnet
            }
            serviceEndpoints: subnet.serviceEndpoints // Define service endpoints (if any)
            privateEndpointNetworkPolicies: subnet.privateEndpointNetworkPolicies // Configure private endpoint policies
            privateLinkServiceNetworkPolicies: subnet.privateLinkServiceNetworkPolicies // Configure private link service policies
          }
}]


@description('The resource ID of the virtual network')
output vnetId string = virtualNetwork.id
