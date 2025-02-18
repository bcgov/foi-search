@description('Main deployment parameters')

param subscription object

// Netwrk Security groups (nsg) parameters
param nsgConfigs array

// vnet parameters

param vnetName string

@description('Array of subnets with offset and mask')
param subnets array

// Asg Parameters

@description('The name of the Application Security Group (ASG)')
param asgName string

@description('The location where the ASG will be created')
param location string

@description('Tags to be applied to the ASG')
param tags object

// nic Parameter

@description('nicConfig')
param nicConfig object
param vmSubnetName string


//doc Intel
param docIntel object

//vmConfig

param vmConfig object
@secure()
param vmAdminPassword string 

//pe config
param peConfig object
param docIntelSubnet string

// bastion config
param bastionConfig object
param bastionSubnet string
param publicIpConfig object


module nsgs 'modules/nsgs.bicep' = {
  name: 'nsgsDeployment'
  params: {
    nsgConfigs: nsgConfigs
  }
}

// Map NSGs to IDs
var nsgMapping = reduce(nsgs.outputs.nsgs, {}, (cur, next) => union(cur, {
  '${next.nsgName}': next.id
}))



module vnet 'modules/vnet.bicep' = {
  name: 'vnetDeployment'
  params: {
    vnetName: vnetName
    subnets: subnets
    nsgMapping: nsgMapping
  }
  dependsOn: [nsgs]
}

module asg 'modules/asg.bicep' = {
  name: 'asgDeployment'
  params: { 
    asgName: asgName 
    location: location 
    tags: tags 
  }
  dependsOn: [vnet]
}



module nic 'modules/nic.bicep' = {
  name: 'nicDeployment'
  params:{
    location: location
    nicConfig: nicConfig
    subnetId: '/subscriptions/${subscription.sub_id}/resourceGroups/${subscription.resourceGroup}/providers/Microsoft.Network/virtualNetworks/${vnetName}/subnets/${vmSubnetName}'
  }
  dependsOn: [
    vnet
  ]
  }

module documentIntelligence 'modules/docIntel.bicep' = {name: 'docIntelDeployment', params:{docIntel:docIntel, location:location}}

module vm 'modules/vm.bicep' = {
  name: 'vmDeployment'
  params: {
    location: location
    vmConfig: vmConfig
    adminPassword: vmAdminPassword
    networkInterfaceId: '/subscriptions/${subscription.sub_id}/resourceGroups/${subscription.resourceGroup}/providers/Microsoft.Network/networkInterfaces/${nicConfig.name}'
  }
  dependsOn: [nic]
}

module privateEndpoint 'modules/pvt-ep.bicep' = {
  name: 'privateEndpoinDeployment'
  params: {
    location: location
    applicationSecurityGroups: [{
      id: '/subscriptions/${subscription.sub_id}/resourceGroups/${subscription.resourceGroup}/providers/Microsoft.Network/applicationSecurityGroups/${asgName}'
    }]
    peConfig: peConfig
    privateLinkServiceId: '/subscriptions/${subscription.sub_id}/resourceGroups/${subscription.resourceGroup}/providers/Microsoft.CognitiveServices/accounts/${docIntel.name}'
    subnetId: '/subscriptions/${subscription.sub_id}/resourceGroups/${subscription.resourceGroup}/providers/Microsoft.Network/virtualNetworks/${vnetName}/subnets/${docIntelSubnet}'
  }
  dependsOn:[vnet, nic, documentIntelligence]
}

module bastion 'modules/bastion.bicep' = {
  name: 'bastionDeployment'
  params: {
    location: location
    bastionConfig: bastionConfig
    publicIpConfig: publicIpConfig
    subnetId: '/subscriptions/${subscription.sub_id}/resourceGroups/${subscription.resourceGroup}/providers/Microsoft.Network/virtualNetworks/${vnetName}/subnets/${bastionSubnet}'
  }
  dependsOn: [vnet]
}
  

