@description('Deploy MCP Server to Azure with enterprise features')
param location string = resourceGroup().location
param environment string = 'dev'
param appName string = 'mcp-server'

@description('Application Insights Connection String')
param appInsightsConnectionString string = ''

@description('Key Vault URL for secrets')
param keyVaultUrl string = ''

@description('Container Registry for Docker images')
param containerRegistryName string

var resourceNamePrefix = '${appName}-${environment}'
var storageAccountName = '${resourceNamePrefix}stor${uniqueString(resourceGroup().id)}'
var cosmosAccountName = '${resourceNamePrefix}-cosmos'
var redisCacheName = '${resourceNamePrefix}-redis'
var containerInstanceName = '${resourceNamePrefix}-aci'
var logAnalyticsWorkspaceName = '${resourceNamePrefix}-logs'
var appInsightsName = '${resourceNamePrefix}-insights'

// Log Analytics Workspace
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsWorkspaceName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      searchVersion: 1
      legacy: 0
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
    IngestionMode: 'LogAnalytics'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// Storage Account for Blob Storage
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    dnsEndpointType: 'Standard'
    defaultToOAuthAuthentication: false
    publicNetworkAccess: 'Enabled'
    allowCrossTenantReplication: false
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true
    networkAcls: {
      bypass: 'AzureServices'
      virtualNetworkRules: []
      ipRules: []
      defaultAction: 'Allow'
    }
    supportsHttpsTrafficOnly: true
    encryption: {
      requireInfrastructureEncryption: false
      services: {
        file: {
          keyType: 'Account'
          enabled: true
        }
        blob: {
          keyType: 'Account'
          enabled: true
        }
      }
      keySource: 'Microsoft.Storage'
    }
    accessTier: 'Hot'
  }
}

// Blob Service
resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  name: 'default'
  parent: storageAccount
  properties: {
    changeFeed: {
      enabled: false
    }
    restorePolicy: {
      enabled: false
    }
    containerDeleteRetentionPolicy: {
      enabled: true
      days: 7
    }
    cors: {
      corsRules: []
    }
    deleteRetentionPolicy: {
      enabled: true
      days: 7
    }
    isVersioningEnabled: false
  }
}

// Container for Copilot resources
resource copilotResourcesContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: 'copilot-resources'
  parent: blobService
  properties: {
    immutableStorageWithVersioning: {
      enabled: false
    }
    defaultEncryptionScope: '$account-encryption-key'
    denyEncryptionScopeOverride: false
    publicAccess: 'None'
  }
}

// Cosmos DB Account
resource cosmosDbAccount 'Microsoft.DocumentDB/databaseAccounts@2023-11-15' = {
  name: cosmosAccountName
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    enableFreeTier: environment == 'dev'
    databaseAccountOfferType: 'Standard'
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    capabilities: [
      {
        name: 'EnableServerless'
      }
    ]
    backupPolicy: {
      type: 'Periodic'
      periodicModeProperties: {
        backupIntervalInMinutes: 240
        backupRetentionIntervalInHours: 8
        backupStorageRedundancy: 'Local'
      }
    }
  }
}

// Cosmos DB Database
resource cosmosDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-11-15' = {
  name: 'mcp-audit'
  parent: cosmosDbAccount
  properties: {
    resource: {
      id: 'mcp-audit'
    }
  }
}

// Cosmos DB Container
resource cosmosContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-11-15' = {
  name: 'audit-events'
  parent: cosmosDatabase
  properties: {
    resource: {
      id: 'audit-events'
      partitionKey: {
        paths: [
          '/tenant_id'
        ]
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        automatic: true
        includedPaths: [
          {
            path: '/*'
          }
        ]
        excludedPaths: [
          {
            path: '/"_etag"/?'
          }
        ]
      }
      defaultTtl: 2592000 // 30 days
    }
  }
}

// Redis Cache
resource redisCache 'Microsoft.Cache/redis@2023-08-01' = {
  name: redisCacheName
  location: location
  properties: {
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
    sku: {
      capacity: environment == 'prod' ? 1 : 0
      family: environment == 'prod' ? 'C' : 'C'
      name: environment == 'prod' ? 'Standard' : 'Basic'
    }
    redisConfiguration: {
      'maxclients': '1000'
      'maxmemory-reserved': '50'
      'maxfragmentationmemory-reserved': '50'
      'maxmemory-delta': '50'
    }
  }
}

// Container Registry (if not provided)
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' = if (empty(containerRegistryName)) {
  name: '${resourceNamePrefix}acr${uniqueString(resourceGroup().id)}'
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
    policies: {
      quarantinePolicy: {
        status: 'disabled'
      }
      trustPolicy: {
        type: 'Notary'
        status: 'disabled'
      }
      retentionPolicy: {
        days: 7
        status: 'disabled'
      }
      exportPolicy: {
        status: 'enabled'
      }
      azureADAuthenticationAsArmPolicy: {
        status: 'enabled'
      }
      softDeletePolicy: {
        retentionDays: 7
        status: 'disabled'
      }
    }
    encryption: {
      status: 'disabled'
    }
    dataEndpointEnabled: false
    publicNetworkAccess: 'Enabled'
    networkRuleBypassOptions: 'AzureServices'
    zoneRedundancy: 'Disabled'
    anonymousPullEnabled: false
  }
}

// Container Instance
resource containerInstance 'Microsoft.ContainerInstance/containerGroups@2023-05-01' = {
  name: containerInstanceName
  location: location
  properties: {
    sku: 'Standard'
    containers: [
      {
        name: 'mcp-server'
        properties: {
          image: empty(containerRegistryName) ? '${containerRegistry.properties.loginServer}/mcp-server:latest' : '${containerRegistryName}.azurecr.io/mcp-server:latest'
          ports: [
            {
              protocol: 'TCP'
              port: 8080
            }
          ]
          environmentVariables: [
            {
              name: 'MCP_HOST'
              value: '0.0.0.0'
            }
            {
              name: 'MCP_PORT'
              value: '8080'
            }
            {
              name: 'MCP_WORKERS'
              value: environment == 'prod' ? '4' : '2'
            }
            {
              name: 'AZURE_STORAGE_CONNECTION_STRING'
              secureValue: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=${az.environment().suffixes.storage}'
            }
            {
              name: 'AZURE_STORAGE_ACCOUNT_NAME'
              value: storageAccount.name
            }
            {
              name: 'AZURE_STORAGE_CONTAINER_NAME'
              value: 'copilot-resources'
            }
            {
              name: 'REDIS_HOST'
              value: redisCache.properties.hostName
            }
            {
              name: 'REDIS_PORT'
              value: '6380'
            }
            {
              name: 'REDIS_PASSWORD'
              secureValue: redisCache.listKeys().primaryKey
            }
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              value: empty(appInsightsConnectionString) ? appInsights.properties.ConnectionString : appInsightsConnectionString
            }
            {
              name: 'AZURE_KEY_VAULT_URL'
              value: keyVaultUrl
            }
            {
              name: 'ENABLE_CACHING'
              value: 'true'
            }
            {
              name: 'ENABLE_AUDIT_LOGGING'
              value: 'true'
            }
            {
              name: 'COSMOS_ENDPOINT'
              value: cosmosDbAccount.properties.documentEndpoint
            }
            {
              name: 'COSMOS_KEY'
              secureValue: cosmosDbAccount.listKeys().primaryMasterKey
            }
          ]
          resources: {
            requests: {
              memoryInGB: json('2.0')
              cpu: json('1.0')
            }
          }
          livenessProbe: {
            httpGet: {
              path: '/health'
              port: 8080
              scheme: 'HTTP'
            }
            initialDelaySeconds: 30
            periodSeconds: 10
            failureThreshold: 3
            successThreshold: 1
            timeoutSeconds: 5
          }
          readinessProbe: {
            httpGet: {
              path: '/health'
              port: 8080
              scheme: 'HTTP'
            }
            initialDelaySeconds: 5
            periodSeconds: 5
            failureThreshold: 3
            successThreshold: 1
            timeoutSeconds: 3
          }
        }
      }
    ]
    imageRegistryCredentials: [
      {
        server: empty(containerRegistryName) ? containerRegistry.properties.loginServer : '${containerRegistryName}.azurecr.io'
        username: empty(containerRegistryName) ? containerRegistry.name : containerRegistryName
        password: empty(containerRegistryName) ? containerRegistry.listCredentials().passwords[0].value : ''
      }
    ]
    restartPolicy: 'Always'
    ipAddress: {
      ports: [
        {
          protocol: 'TCP'
          port: 8080
        }
      ]
      type: 'Public'
      dnsNameLabel: containerInstanceName
    }
    osType: 'Linux'
    diagnostics: {
      logAnalytics: {
        workspaceId: logAnalytics.properties.customerId
        workspaceKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

// Outputs
output mcpServerUrl string = 'http://${containerInstance.properties.ipAddress.fqdn}:8080'
output storageAccountName string = storageAccount.name
output redisHostName string = redisCache.properties.hostName
output cosmosDbEndpoint string = cosmosDbAccount.properties.documentEndpoint
output appInsightsConnectionString string = appInsights.properties.ConnectionString
output containerRegistryLoginServer string = empty(containerRegistryName) ? containerRegistry.properties.loginServer : '${containerRegistryName}.azurecr.io'
