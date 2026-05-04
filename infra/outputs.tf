# acr 
output "acr_username" { 
  value = azurerm_container_registry.main.admin_username
  # sensitive = true
}

output "acr_password" { 
  value = azurerm_container_registry.main.admin_password
  sensitive = true
}

# Container app 
output "container_app_name" {
  value = azurerm_container_app.main.name
}

output "container_app_resource_group" {
  value = azurerm_container_app.main.resource_group_name
}

# Storage account 
output "storage_account_name" {
  value = azurerm_storage_account.main.name 
}

output "storage_account_key" {
  value = azurerm_storage_account.main.primary_access_key
  sensitive = true
}

# AML workspace
output "aml_workspace_name" {
  value = azurerm_machine_learning_workspace.main.name
}

output "aml_resource_group" {
  value = azurerm_machine_learning_workspace.main.resource_group_name 
}

# container app 
output "container_app_url" {
  value = azurerm_container_app.main.latest_revision_fqdn
  
}

output "container_login_server" {
  value = azurerm_container_registry.main.login_server
}