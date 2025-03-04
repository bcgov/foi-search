// Parameter for Virtual Machine configuration object
param vmConfig object

// Parameter for the Network Interface ID to attach to the VM
param networkInterfaceId string

// Secure parameter for the Virtual Machine admin password
@secure()
param adminPassword string

// Parameter for the Virtual Machine admin username
param adminUsername string

// Parameter for the location where the VM will be deployed
param location string

// Define the Virtual Machine resource
resource vm 'Microsoft.Compute/virtualMachines@2023-07-01' = {
  name: vmConfig.vmName
  location: location
  properties: {
    // Hardware configuration (e.g., VM size)
    hardwareProfile: {
      vmSize: vmConfig.vmSize
    }

    // Storage configuration for the OS disk
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

    // OS profile (credentials and OS settings)
    osProfile: {
      computerName: vmConfig.vmName
      adminUsername: adminUsername
      adminPassword: adminPassword
      windowsConfiguration: {
        provisionVMAgent: true // Ensures Azure VM agent is installed
      }
      allowExtensionOperations: true
    }

    // Network configuration to attach the NIC
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

    // Diagnostics configuration for boot diagnostics
    diagnosticsProfile: {
      bootDiagnostics: {
        enabled: true
      }
    }

    // License type for the VM (e.g., Windows_Client)
    licenseType: vmConfig.licenseType
  }
}
