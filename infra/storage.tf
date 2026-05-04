

resource "azurerm_storage_account" "main" {
  name = "${local.safe_prefix}storages"
  resource_group_name = azurerm_resource_group.main.name
  location = azurerm_resource_group.main.location
  account_tier = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "video_demo" {
  name = "video-demo"
  storage_account_id = azurerm_storage_account.main.id
  container_access_type = "private"
}

resource "azurerm_storage_container" "predictions_log" {
  name = "predictions-log"
  storage_account_id = azurerm_storage_account.main.id
  container_access_type = "private"
}