data "azurerm_client_config" "current" {}


resource "azurerm_resource_group" "main" {
  name = "${var.prefix}-rg"
  location = var.location
}

resource "azurerm_resource_group" "aml" {
  name = "${var.aml_workspace_name}-rg"
  location = var.location
}