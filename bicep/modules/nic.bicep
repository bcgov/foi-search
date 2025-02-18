@description('Array of Network Interface configurations')
param nicConfig object

@description('The location where all NICs will be deployed')
param location string

param subnetId string

resource nics 'Microsoft.Network/networkInterfaces@2024-03-01' = {
  name: nicConfig.name
  location: location
  properties: {
    ipConfigurations: [
      {
        name: nicConfig.ipConfig.name
        properties: {
          privateIPAllocationMethod: nicConfig.ipConfig.privateIPAllocationMethod
          subnet: {
            id: subnetId
          }
          primary: nicConfig.ipConfig.primary
          privateIPAddressVersion: nicConfig.ipConfig.privateIPAddressVersion
        }
      }
    ]
    enableAcceleratedNetworking: nicConfig.enableAcceleratedNetworking
  }
}

