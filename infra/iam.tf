resource "azurerm_role_assignment" "acr_pull" { # assign ACR Pull role to Container App, so that it can pull image from ACR
  scope                = azurerm_container_registry.main.id 
  role_definition_name = "AcrPull"
  principal_id         = azurerm_container_app.main.identity[0].principal_id
}

# resource "azurerm_role_assignment" "storage_blob" { # assign Storage Blob Data Contributor role to Container App, so that it can read/write blob in storage account, you can also assign more granular role like Storage Blob Data Reader or Storage Blob Data Writer based on your need
#   scope                = azurerm_storage_account.main.id 
#   role_definition_name = "Storage Blob Data Contributor"
#   principal_id         = azurerm_container_app.main.identity[0].principal_id
# }