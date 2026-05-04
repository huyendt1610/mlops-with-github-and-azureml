#!/bin/bash
ENV=${1:-dev} # default to dev if no argument is provided at position 1
AUTO_APPROVE=${2:-""} # default to false if no argument is provided at position 2

terraform init -backend-config="environments/$ENV.backend.tfvars" -reconfigure
terraform apply -var-file="environments/$ENV.tfvars"  $AUTO_APPROVE

# Usage:
# ./deploy.sh dev # local 
# ./deploy.sh prod -auto-approve # CI/CD