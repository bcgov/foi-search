// Name of the Virtual Machine
param vmConfig object

// Network Interface ID to attach to the VM
param networkInterfaceId string

@secure()
param adminPassword string

param location string

// Virtual Machine Resource
resource vm 'Microsoft.Compute/virtualMachines@2023-07-01' = {
  name: vmConfig.vmName
  location: location
  properties: {
    // Hardware configuration
    hardwareProfile: {
      vmSize: vmConfig.vmSize
    }

    // Storage configuration
    storageProfile: {
      imageReference: vmConfig.imageReference
      osDisk: {
        osType: 'Windows'
        name: '${vmConfig.vmName}_OsDisk'
        createOption: 'FromImage'
        managedDisk: {
          storageAccountType: vmConfig.storageAccountType
        }
        diskSizeGB: vmConfig.osDiskSizeGB
      }
    }

    // OS profile (user credentials and OS settings)
    osProfile: {
      computerName: vmConfig.vmName
      adminUsername: vmConfig.adminUsername
      adminPassword: adminPassword
      windowsConfiguration: {
        provisionVMAgent: true // Ensures Azure VM agent is installed
      }
      allowExtensionOperations: true
    }

    // Network configuration
    networkProfile: {
      networkInterfaces: [
        {
          id: networkInterfaceId
          properties: {
            deleteOption: 'Delete' // Ensures NIC is deleted when VM is deleted
          }
        }
      ]
    }

    // Enable boot diagnostics
    diagnosticsProfile: {
      bootDiagnostics: {
        enabled: true
      }
    }

    // License type for the VM
    licenseType: vmConfig.licenseType
  }
}
