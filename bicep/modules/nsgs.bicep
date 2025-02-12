@description('Array of Network Security Groups (NSGs) with their configurations')
param nsgConfigs array

resource nsgs 'Microsoft.Network/networkSecurityGroups@2024-05-01' = [for nsgConfig in nsgConfigs: {
  name: nsgConfig.nsgName
  location: nsgConfig.location
  tags: nsgConfig.tags
  properties: {
    securityRules: [for rule in nsgConfig.securityRules: {
      name: rule.name
      properties: {
        protocol: rule.protocol
        sourcePortRange: rule.sourcePortRange
        destinationPortRanges: rule.destinationPortRanges  // Use PortRanges array
        sourceAddressPrefix: rule.sourceAddressPrefix
        destinationAddressPrefix: rule.destinationAddressPrefix
        access: rule.access
        priority: rule.priority
        direction: rule.direction
      }
    }]
  }
}]

// Output the NSG IDs in an array format
// output nsgIds array = [for i in range(0, length(nsgConfigs)): nsgs[i].id]
output nsgs array = [for i in range(0, length(nsgConfigs)): {
  nsgName: nsgs[i].name
  id: nsgs[i].id
}]
