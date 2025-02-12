@description('Array of Network Interface configurations')
param nicConfigs array

@description('The location where all NICs will be deployed')
param location string

resource nics 'Microsoft.Network/networkInterfaces@2024-03-01' = [for nic in nicConfigs: {
  name: nic.name
  location: location
  tags: nic.tags
  properties: {
    ipConfigurations: [
      {
        name: nic.ipConfig.name
        properties: {
          privateIPAllocationMethod: nic.ipConfig.privateIPAllocationMethod
          subnet: {
            id: nic.ipConfig.subnetId
          }
          primary: nic.ipConfig.primary
          privateIPAddressVersion: nic.ipConfig.privateIPAddressVersion
        }
      }
    ]
    enableAcceleratedNetworking: nic.enableAcceleratedNetworking
  }
}]

