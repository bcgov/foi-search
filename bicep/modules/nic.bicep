@description('Array of Network Interface configurations')
param nicConfig object

@description('The location where all NICs will be deployed')
param location string

@description('Subnet ID where the NIC will be deployed')
param subnetId string

// Create a Network Interface resource
resource nics 'Microsoft.Network/networkInterfaces@2024-03-01' = {
  name: nicConfig.name
  location: location
  properties: {
    ipConfigurations: [
      {
        name: nicConfig.ipConfig.name
        properties: {
          // Defines how the private IP is allocated (Dynamic by default)
          privateIPAllocationMethod: nicConfig.ipConfig.privateIPAllocationMethod

          // Assign the NIC to a specific subnet
          subnet: {
            id: subnetId
          }

          // Indicates whether this IP configuration is the primary one
          primary: nicConfig.ipConfig.primary

          // Defines the IP version (IPv4 or IPv6)
          privateIPAddressVersion: nicConfig.ipConfig.privateIPAddressVersion
        }
      }
    ]

    // Enables or disables accelerated networking for the NIC
    enableAcceleratedNetworking: nicConfig.enableAcceleratedNetworking
  }
}
