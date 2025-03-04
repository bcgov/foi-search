// Name of the Azure Bastion host
param bastionConfig object
param publicIpConfig object
param bastionName string

// Deployment location
param location string

// Subnet ID where Bastion will be deployed
param subnetId string

// Public IP resource for Bastion
resource publicIp 'Microsoft.Network/publicIPAddresses@2024-05-01' = {
  name: publicIpConfig.name
  location: location
  sku: {
    name: publicIpConfig.sku
  }
  properties: {
    publicIPAllocationMethod: publicIpConfig.allocationMethod
  }
}

// Azure Bastion host resource
resource bastion 'Microsoft.Network/bastionHosts@2024-05-01' = {
  name: bastionName
  location: location
  sku: {
    name: bastionConfig.skuName
  }
  properties: {
    scaleUnits: bastionConfig.scaleUnits
    ipConfigurations: [
      {
        name: 'IpConf'
        properties: {
          publicIPAddress: {
            id: publicIp.id // Dynamically references Public IP resource
          }
          subnet: {
            id: subnetId
          }
        }
      }
    ]
  }
}
