@description('The name of the Application Security Group (ASG)')
param asgName string

@description('The location where the ASG will be created')
param location string 


resource applicationSecurityGroup 'Microsoft.Network/applicationSecurityGroups@2024-05-01' = {
  name: asgName
  location: location
  properties: {}
}

@description('The resource ID of the Application Security Group')
output asgId string = applicationSecurityGroup.id
