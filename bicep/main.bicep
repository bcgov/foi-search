@description('Main deployment parameters')
param subId string

param licencePlate string

param environment string

param resourceGroup string = '${licencePlate}-${environment}-networking'

// Netwrk Security groups (nsg) parameters
param nsgConfigs array

// vnet parameters

param vnetName string = '${licencePlate}-${environment}-vwan-spoke'

@description('Array of subnets with offset and mask')
param subnets array

// Asg Parameters

@description('The name of the Application Security Group (ASG)')
param asgName string

@description('The location where the ASG will be created')
param location string

// nic Parameter

@description('nicConfig')
param nicConfig object
param vmSubnetName string

//doc Intel
param docIntelName string = 'foidocintelservice-${environment}'
param docIntelConfig object

//vmConfig

param vmConfig object
@secure()
param vmAdminPassword string
param vmAdminUsername string

//pe config
param peConfig object
param docIntelSubnet string

// bastion config
param bastionName string = '${licencePlate}-${environment}-vwan-spoke-bastion'
param bastionConfig object
param bastionSubnet string
param publicIpConfig object

module nsgs 'modules/nsgs.bicep' = {
  name: 'nsgsDeployment'
  params: {
    nsgConfigs: nsgConfigs
  }
}

module vnet 'modules/vnet.bicep' = {
  name: 'vnetDeployment'
  params: {
    vnetName: vnetName
    subnets: subnets
    nsgArray: nsgs.outputs.nsgs
  }
  dependsOn: [nsgs]
}

module asg 'modules/asg.bicep' = {
  name: 'asgDeployment'
  params: {
    asgName: asgName
    location: location
  }
  dependsOn: [vnet]
}

module nic 'modules/nic.bicep' = {
  name: 'nicDeployment'
  params: {
    location: location
    nicConfig: nicConfig
    subnetId: '/subscriptions/${subId}/resourceGroups/${subId}/providers/Microsoft.Network/virtualNetworks/${vnetName}/subnets/${vmSubnetName}'
  }
  dependsOn: [vnet]
}

module documentIntelligence 'modules/docIntel.bicep' = {
  name: 'docIntelDeployment'
  params: { docIntelConfig: docIntelConfig, location: location , docIntelName: docIntelName}
}

module vm 'modules/vm.bicep' = {
  name: 'vmDeployment'
  params: {
    location: location
    vmConfig: vmConfig
    adminPassword: vmAdminPassword
    adminUsername: vmAdminUsername
    networkInterfaceId: '/subscriptions/${subId}/resourceGroups/${resourceGroup}/providers/Microsoft.Network/networkInterfaces/${nicConfig.name}'
  }
  dependsOn: [nic]
}

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
  dependsOn: [vnet, nic, documentIntelligence]
}

module bastion 'modules/bastion.bicep' = {
  name: 'bastionDeployment'
  params: {
    location: location
    bastionConfig: bastionConfig
    bastionName: bastionName
    publicIpConfig: publicIpConfig
    subnetId: '/subscriptions/${subId}/resourceGroups/${resourceGroup}/providers/Microsoft.Network/virtualNetworks/${vnetName}/subnets/${bastionSubnet}'
  }
  dependsOn: [vnet]
}
