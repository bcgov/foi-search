// Name of the Virtual Machine
param vmName string

// Deployment location (default is resource group location)
param location string

// Administrator username for the VM
param adminUsername string

// Secure password for the administrator user
@secure()
param adminPassword string

// Size of the VM (e.g., Standard_D2s_v3)
param vmSize string

// Image reference for the OS (publisher, offer, SKU, version)
param imageReference object

// OS Disk size in GB
param osDiskSizeGB int

// Storage account type for the OS disk (e.g., Premium_LRS, Standard_LRS)
param storageAccountType string

// Network Interface ID to attach to the VM
param networkInterfaceId string

// License type (e.g., Windows_Client, Windows_Server)
param licenseType string

// Virtual Machine Resource
resource vm 'Microsoft.Compute/virtualMachines@2023-07-01' = {
  name: vmName
  location: location
  properties: {
    // Hardware configuration
    hardwareProfile: {
      vmSize: vmSize
    }

    // Storage configuration
    storageProfile: {
      imageReference: imageReference
      osDisk: {
        osType: 'Windows'
        name: '${vmName}_OsDisk'
        createOption: 'FromImage'
        managedDisk: {
          storageAccountType: storageAccountType
        }
        diskSizeGB: osDiskSizeGB
      }
    }

    // OS profile (user credentials and OS settings)
    osProfile: {
      computerName: vmName
      adminUsername: adminUsername
      adminPassword: adminPassword
      windowsConfiguration: {
        provisionVMAgent: true // Ensures Azure VM agent is installed
      }
      secrets: []
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
    licenseType: licenseType
  }
}
