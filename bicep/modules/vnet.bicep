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


// Deploy first subnet
resource subnet0 'Microsoft.Network/virtualNetworks/subnets@2024-05-01' = if (length(updatedSubnets) > 0) {
  parent: virtualNetwork
  name: updatedSubnets[0].name
  properties: {
    addressPrefix: '${ipOctets[0]}.${ipOctets[1]}.${ipOctets[2]}.${int(ipOctets[3]) + updatedSubnets[0].offset}/${updatedSubnets[0].mask}'
    networkSecurityGroup: {
      id: updatedSubnets[0].networkSecurityGroupId
    }
    serviceEndpoints: updatedSubnets[0].serviceEndpoints
    privateEndpointNetworkPolicies: updatedSubnets[0].privateEndpointNetworkPolicies
    privateLinkServiceNetworkPolicies: updatedSubnets[0].privateLinkServiceNetworkPolicies
  }
}

// Deploy second subnet, depending on first
resource subnet1 'Microsoft.Network/virtualNetworks/subnets@2024-05-01' = if (length(updatedSubnets) > 1) {
  parent: virtualNetwork
  name: updatedSubnets[1].name
  properties: {
    addressPrefix: '${ipOctets[0]}.${ipOctets[1]}.${ipOctets[2]}.${int(ipOctets[3]) + updatedSubnets[1].offset}/${updatedSubnets[1].mask}'
    networkSecurityGroup: {
      id: updatedSubnets[1].networkSecurityGroupId
    } 
    serviceEndpoints: updatedSubnets[1].serviceEndpoints
    privateEndpointNetworkPolicies: updatedSubnets[1].privateEndpointNetworkPolicies
    privateLinkServiceNetworkPolicies: updatedSubnets[1].privateLinkServiceNetworkPolicies
  }
  dependsOn: [
    subnet0
  ]
}

// Deploy third subnet, depending on second
resource subnet2 'Microsoft.Network/virtualNetworks/subnets@2024-05-01' = if (length(updatedSubnets) > 2) {
  parent: virtualNetwork
  name: updatedSubnets[2].name
  properties: {
    addressPrefix: '${ipOctets[0]}.${ipOctets[1]}.${ipOctets[2]}.${int(ipOctets[3]) + updatedSubnets[2].offset}/${updatedSubnets[2].mask}'
    networkSecurityGroup: {
      id: updatedSubnets[2].networkSecurityGroupId
    } 
    serviceEndpoints: updatedSubnets[2].serviceEndpoints
    privateEndpointNetworkPolicies: updatedSubnets[2].privateEndpointNetworkPolicies
    privateLinkServiceNetworkPolicies: updatedSubnets[2].privateLinkServiceNetworkPolicies
  }
  dependsOn: [
    subnet1
  ]
}

// Output the virtual network ID
output vnetId string = virtualNetwork.id
