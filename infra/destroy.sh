#!/bin/bash
ENV=${1:-dev}

terraform init -backend-config="environments/$ENV.backend.tfvars" -reconfigure
terraform destroy -var-file="environments/$ENV.tfvars"

# Usage:
# ./destroy.sh dev
# ./destroy.sh prod
