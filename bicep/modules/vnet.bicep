// Parameter for the name of the virtual network
param vnetName string

// Parameter for an array of subnets with necessary details like offset and mask
param subnets array

// Parameter for an array of NSG configurations
param nsgArray array

// Create a mapping of NSGs to their respective IDs
var nsgMapping = reduce(nsgArray, {}, (cur, next) => union(cur, {
  '${next.nsgName}': next.id
}))

// Reference the existing virtual network
resource virtualNetwork 'Microsoft.Network/virtualNetworks@2024-05-01' existing = {
  name: vnetName
}

// Process and update subnets with corresponding NSG IDs
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

// Extract the base IP address from the address space of the VNet
var addressSpace = virtualNetwork.properties.addressSpace.addressPrefixes[0]
var cidrParts = split(addressSpace, '/')
var baseIP = cidrParts[0]
var ipOctets = split(baseIP, '.')

// Create subnets based on the updated subnet configurations
resource subnetDeployment 'Microsoft.Network/virtualNetworks/subnets@2024-05-01' = [for subnet in updatedSubnets: {
  parent: virtualNetwork
  name: subnet.name
  properties: {
    // Calculate the subnet address range using the base IP and subnet offset/mask
    addressPrefix: '${ipOctets[0]}.${ipOctets[1]}.${ipOctets[2]}.${int(ipOctets[3]) + subnet.offset}/${subnet.mask}'
    networkSecurityGroup: {
      id: subnet.networkSecurityGroupId // Assign NSG ID to the subnet
    }
    serviceEndpoints: subnet.serviceEndpoints // Attach any service endpoints to the subnet
    privateEndpointNetworkPolicies: subnet.privateEndpointNetworkPolicies // Define private endpoint policies
    privateLinkServiceNetworkPolicies: subnet.privateLinkServiceNetworkPolicies // Define private link service policies
  }
}]

// Output the virtual network ID
output vnetId string = virtualNetwork.id
