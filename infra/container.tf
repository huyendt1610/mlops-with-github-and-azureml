resource "azurerm_container_registry" "main" {
  name = "${local.safe_acr_name}"
  resource_group_name = azurerm_resource_group.main.name
  location = azurerm_resource_group.main.location
  sku = "Basic"
  admin_enabled = false# true if you want to use admin account, but it's recommended to use service principal or managed identity for authentication in production
}

# container app
resource "azurerm_container_app_environment" "main" {
  name                = "${local.safe_prefix}containerenv"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
}

resource "azurerm_container_app" "main" {
  name                = "${local.safe_prefix}containerapp"
  resource_group_name = azurerm_resource_group.main.name
  # location            = azurerm_resource_group.main.location # auto get from environment
  container_app_environment_id = azurerm_container_app_environment.main.id
  revision_mode = "Single"

  # for admin account auth, not recommended for production
  # registry {
  #   server = azurerm_container_registry.main.login_server
  #   username = azurerm_container_registry.main.admin_username
  #   password_secret_name = "acr-password"
  # }

  # secret {
  #   name = "acr-password"
  #   value = azurerm_container_registry.main.admin_password
  # }

  registry {
    server = azurerm_container_registry.main.login_server 
    identity = "System"
  }

  ingress {
    external_enabled = true
    target_port      = 8000
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  template {
    container {
      name   = "chicagoticket-app"
      image  = "${azurerm_container_registry.main.login_server}/chicagoticket-app:latest"
      #image = "nginx:latest"
      cpu    = "0.5"
      memory = "1.0Gi"
    }
    min_replicas = 0 
    max_replicas = 3
  }

  tags = {
    environment = var.environment
  }

  timeouts {
    create = "15m"
    update = "15m"
    delete = "15m"
  }

  identity {
    type = "SystemAssigned"
  }
}