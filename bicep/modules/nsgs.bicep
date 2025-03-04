@description('Array of Network Security Groups (NSGs) with their configurations')
param nsgConfigs array

// Deploy multiple Network Security Groups (NSGs) based on input configurations
resource nsgs 'Microsoft.Network/networkSecurityGroups@2024-05-01' = [for nsgConfig in nsgConfigs: {
  name: nsgConfig.nsgName
  location: nsgConfig.location
  properties: {
    securityRules: [for rule in nsgConfig.securityRules: {
      name: rule.name
      properties: {
        // Define protocol (TCP, UDP, or *)
        protocol: rule.protocol

        // Define allowed source and destination port ranges
        sourcePortRange: rule.sourcePortRange
        destinationPortRanges: rule.destinationPortRanges  // Use PortRanges array

        // Define traffic filtering rules
        sourceAddressPrefix: rule.sourceAddressPrefix
        destinationAddressPrefix: rule.destinationAddressPrefix

        // Allow or deny traffic based on rule
        access: rule.access

        // Rule priority (lower number = higher priority)
        priority: rule.priority

        // Traffic direction (Inbound or Outbound)
        direction: rule.direction
      }
    }]
  }
}]

// Output the NSG names and IDs for reference
output nsgs array = [for i in range(0, length(nsgConfigs)): {
  nsgName: nsgs[i].name
  id: nsgs[i].id
}]
