// Main deployment parameters
@description('Subscription ID for the deployment')
param subId string

@description('Licence plate for the environment')
param licencePlate string

@description('Environment identifier (e.g., dev, prod)')
param environment string

@description('Resource Group name for networking resources')
param resourceGroup string = '${licencePlate}-${environment}-networking'

// Network Security Groups (NSG) parameters
@description('Array of NSG configurations')
param nsgConfigs array

// Virtual Network (VNet) parameters
@description('Name of the virtual network (VNet) for deployment')
param vnetName string = '${licencePlate}-${environment}-vwan-spoke'

@description('Array of subnets with offset and mask for VNet')
param subnets array

// Application Security Group (ASG) parameters
@description('The name of the Application Security Group (ASG)')
param asgName string

@description('The location where the ASG will be created')
param location string

// Network Interface Card (NIC) parameters
@description('NIC configuration for the virtual machine')
param nicConfig object

@description('The name of the VM subnet')
param vmSubnetName string

// Document Intelligence (Doc Intel) parameters
@description('Name of the Document Intelligence service')
param docIntelName string = 'foidocintelservice-${environment}'

@description('Configuration details for Document Intelligence service')
param docIntelConfig object

// Virtual Machine (VM) parameters
@description('Configuration for the virtual machine')
param vmConfig object

@secure()
@description('Admin password for the VM')
param vmAdminPassword string

@description('Admin username for the VM')
param vmAdminUsername string

// Private Endpoint (PE) parameters
@description('Configuration for Private Endpoint')
param peConfig object

@description('The subnet name for Document Intelligence')
param docIntelSubnet string

// Bastion parameters
@description('Name for the Bastion host')
param bastionName string = '${licencePlate}-${environment}-vwan-spoke-bastion'

@description('Configuration for the Bastion host')
param bastionConfig object

@description('The subnet for Bastion')
param bastionSubnet string

@description('Public IP configuration for Bastion')
param publicIpConfig object

// Module for deploying Network Security Groups (NSGs)
module nsgs 'modules/nsgs.bicep' = {
  name: 'nsgsDeployment'
  params: {
    nsgConfigs: nsgConfigs
  }
}

// Module for deploying the Virtual Network (VNet) and its subnets
module vnet 'modules/vnet.bicep' = {
  name: 'vnetDeployment'
  params: {
    vnetName: vnetName
    subnets: subnets
    nsgArray: nsgs.outputs.nsgs // Outputs from the NSGs module
  }
  dependsOn: [nsgs] // Ensure NSGs are deployed before VNet
}

// Module for deploying the Application Security Group (ASG)
module asg 'modules/asg.bicep' = {
  name: 'asgDeployment'
  params: {
    asgName: asgName
    location: location
  }
  dependsOn: [vnet] // Ensure VNet is deployed before ASG
}

// Module for deploying Network Interface Cards (NICs)
module nic 'modules/nic.bicep' = {
  name: 'nicDeployment'
  params: {
    location: location
    nicConfig: nicConfig
    subnetId: '/subscriptions/${subId}/resourceGroups/${subId}/providers/Microsoft.Network/virtualNetworks/${vnetName}/subnets/${vmSubnetName}'
  }
  dependsOn: [vnet] // Ensure VNet is deployed before NIC
}

// Module for deploying Document Intelligence service (Cognitive Services)
module documentIntelligence 'modules/docIntel.bicep' = {
  name: 'docIntelDeployment'
  params: { 
    docIntelConfig: docIntelConfig 
    location: location 
    docIntelName: docIntelName
  }
}

// Module for deploying the Virtual Machine (VM)
module vm 'modules/vm.bicep' = {
  name: 'vmDeployment'
  params: {
    location: location
    vmConfig: vmConfig
    adminPassword: vmAdminPassword
    adminUsername: vmAdminUsername
    networkInterfaceId: '/subscriptions/${subId}/resourceGroups/${resourceGroup}/providers/Microsoft.Network/networkInterfaces/${nicConfig.name}'
  }
  dependsOn: [nic] // Ensure NIC is deployed before VM
}

// Module for deploying the Private Endpoint (PE) for Document Intelligence
module privateEndpoint 'modules/pvt-ep.bicep' = {
  name: 'privateEndpoinDeployment'
  params: {
    location: location
    applicationSecurityGroups: [
      {
        id: '/subscriptions/${subId}/resourceGroups/${resourceGroup}/providers/Microsoft.Network/applicationSecurityGroups/${asgName}'
      }
    ]
    peConfig: peConfig
    privateLinkServiceId: '/subscriptions/${subId}/resourceGroups/${resourceGroup}/providers/Microsoft.CognitiveServices/accounts/${docIntelConfig.name}'
    subnetId: '/subscriptions/${subId}/resourceGroups/${resourceGroup}/providers/Microsoft.Network/virtualNetworks/${vnetName}/subnets/${docIntelSubnet}'
  }
  dependsOn: [vnet, nic, documentIntelligence] // Ensure VNet, NIC, and Doc Intel are deployed before Private Endpoint
}

// Module for deploying Bastion service
module bastion 'modules/bastion.bicep' = {
  name: 'bastionDeployment'
  params: {
    location: location
    bastionConfig: bastionConfig
    bastionName: bastionName
    publicIpConfig: publicIpConfig
    subnetId: '/subscriptions/${subId}/resourceGroups/${resourceGroup}/providers/Microsoft.Network/virtualNetworks/${vnetName}/subnets/${bastionSubnet}'
  }
  dependsOn: [vnet] // Ensure VNet is deployed before Bastion
}
