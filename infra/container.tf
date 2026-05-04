resource "azurerm_container_registry" "main" {
  name = "${local.safe_acr_name}"
  resource_group_name = azurerm_resource_group.main.name
  location = azurerm_resource_group.main.location
  sku = "Basic"
  admin_enabled = true
}

# container app
resource "azurerm_container_environment" "main" {
  name                = "${local.safe_prefix}containerenv"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
}

resource "azurerm_container_app" "main" { 
  name                = "${local.safe_prefix}containerapp"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  container_app_environment_id = azurerm_container_environment.main.id
  revision_mode = "Single"

  registry {
    server = azurerm_container_registry.main.login_server
    username = azurerm_container_registry.main.admin_username
    password_secret_name = "acr-password"
  }

  secret {
    name = "acr-password"
    value = azurerm_container_registry.main.admin_password
  }

  template {
    container {
      name   = "chicagoticket-app"
      image  = "${azurerm_container_registry.main.login_server}/chicagoticket-app:latest"
      cpu    = "0.5"
      memory = "1.0"
    }
  }
  

  tags = {
    environment = var.environment
  }
}