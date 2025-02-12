// Name of the Azure Bastion host
param bastionName string

// Deployment location
param location string

// Subnet ID where Bastion will be deployed
param subnetId string

// SKU of the Bastion host (Basic or Standard)
param skuName string

// Number of scale units for Bastion
param scaleUnits int

// Public IP parameters
param publicIpName string
param allocationMethod string // 'Static' or 'Dynamic'
param sku string // 'Basic' or 'Standard'

// Public IP resource for Bastion
resource publicIp 'Microsoft.Network/publicIPAddresses@2024-05-01' = {
  name: publicIpName
  location: location
  sku: {
    name: sku
  }
  properties: {
    publicIPAllocationMethod: allocationMethod
  }
}

// Azure Bastion host resource
resource bastion 'Microsoft.Network/bastionHosts@2024-05-01' = {
  name: bastionName
  location: location
  sku: {
    name: skuName
  }
  properties: {
    scaleUnits: scaleUnits
    ipConfigurations: [
      {
        name: 'IpConf'
        properties: {
          privateIPAllocationMethod: 'Dynamic'
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
