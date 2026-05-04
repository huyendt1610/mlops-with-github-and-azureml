resource "random_string" "suffix" {
  length = 4
  upper = false
  numeric = true
  special = false
}

resource "azurerm_application_insights" "aml" {
  name = "${local.safe_aml_ws_name}appinsights"
  resource_group_name = azurerm_resource_group.aml.name
  location = azurerm_resource_group.aml.location
  application_type = "web"
}

resource "azurerm_key_vault" "aml" { # name must be globally unique
  name = "${local.substr_key_vault_name}"
  resource_group_name = azurerm_resource_group.aml.name
  location = azurerm_resource_group.aml.location
  tenant_id = data.azurerm_client_config.current.tenant_id
  sku_name = "standard"

  purge_protection_enabled = true
  soft_delete_retention_days = 7
}

resource "azurerm_storage_account" "aml" {
  name = "${local.substr_aml_storage_name}"
  resource_group_name = azurerm_resource_group.aml.name
  location = azurerm_resource_group.aml.location
  account_tier = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_machine_learning_workspace" "main" {
  name = "${local.safe_aml_ws_name}"
  resource_group_name = azurerm_resource_group.aml.name
  location = azurerm_resource_group.aml.location

  application_insights_id = azurerm_application_insights.aml.id # mandatory
  key_vault_id = azurerm_key_vault.aml.id                        # mandatory
  storage_account_id = azurerm_storage_account.aml.id           # mandatory

  container_registry_id = azurerm_container_registry.main.id # optional, but needed if you want to use Azure Container Registry to store your docker images for AzureML
  
  identity {
    type = "SystemAssigned"
  }
}