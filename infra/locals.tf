locals {
  safe_prefix            = replace(var.prefix, "-", "")
  safe_aml_ws_name       = replace(var.aml_workspace_name, "-", "")
  substr_aml_storage_name ="${substr("${local.safe_aml_ws_name}", 0, 14)}storage" # Storage account name: Max length is 24, and must end with "storage".
  substr_key_vault_name = "${substr("${local.safe_aml_ws_name}${random_string.suffix.result}", 0, 21)}kv" # Key vault name: Max length is 24.
  safe_acr_name           = "${substr("${local.safe_prefix}${random_string.suffix.result}", 0, 47)}acr" # ACR name: Max length is 50
}
