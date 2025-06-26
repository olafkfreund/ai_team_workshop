// Advanced Bicep sample for Copilot testing
param environment string = 'dev'
param location string = resourceGroup().location

resource storage 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: 'copilotsample${uniqueString(resourceGroup().id)}'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  tags: {
    environment: environment
  }
}

output storageAccountName string = storage.name
