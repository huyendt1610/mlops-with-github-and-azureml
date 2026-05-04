terraform {
    required_providers {
        azurerm = {
            source  = "hashicorp/azurerm"
            version = "~> 4.0"
        }
        random = {
            source  = "hashicorp/random"
            version = "~> 3.0"
        }
    }

    backend "azurerm" { # auto upload tfstate to Azure Storage, after terraform apply
        resource_group_name  = "tfstate-rg"
        storage_account_name = "tfstatedevticketstorage"
        container_name       = "tfstate"
        key                  = "terraform.tfstate"
      
    }
}

provider "azurerm" { # import & config provider 
  features {}
}