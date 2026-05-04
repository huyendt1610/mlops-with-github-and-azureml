#!/bin/bash
ENV=${1:-dev}
AUTO_APPROVE=${2:-""}

terraform init -backend-config="environments/$ENV.backend.tfvars" -reconfigure
terraform apply -var-file="environments/$ENV.tfvars" $AUTO_APPROVE

# Usage:
# ./deploy.sh dev                      # local
# ./deploy.sh prod -auto-approve       # CI/CD