# MLOps with GitHub and Azure ML

An end-to-end MLOps project demonstrating how to build, train, deploy, and monitor a machine learning model using **Azure Machine Learning**, **GitHub Actions**, and **DVC**. The model predicts the likelihood that a Chicago parking ticket will remain unpaid using a variety of ticket details as inputs.

The label column is `PaymentIsOutstanding`:
- **1** — the ticket is still outstanding; the city was never able to collect full payment and the person still owes money
- **0** — the ticket has been resolved; either the person paid in full or a judge dismissed it in court, leaving the city with no outstanding debt for that ticket

---

## Architecture Overview

```
GitHub Actions (CI/CD)
       │
       ├──► Azure ML Pipeline
       │      ├── Replace Missing Values
       │      ├── Feature Engineering
       │      ├── Feature Selection
       │      ├── Split Data
       │      ├── Train Model  ──► MLflow (metrics + model)
       │      └── Register Model ──► Azure ML Model Registry
       │                                      │
       │                                      ▼
       │                          Azure ML Batch Endpoint
       │                          (ticket-endpoint)
       │
       └──► Build & Push Docker Image
              │
              ▼
        Azure Container Registry (ACR)
              │   tagged: :latest | :model-<hash> | :<git-sha>
              ▼
        Azure Container Apps
        (FastAPI serving app)
              │
              ▼
        Azure Blob Storage
        (predictions-log container)
              │
              ▼
        Drift Monitor (Evidently)
        outputs/drift_report.html
```

Data is versioned with **DVC** and stored on **Azure Data Lake Storage (ADLS)**.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10 |
| ML Framework | scikit-learn (Gradient Boosting Classifier) |
| Cloud Platform | Azure Machine Learning |
| Experiment Tracking | MLflow (integrated with Azure ML) |
| Model Registry | Azure ML + MLflow |
| Data Versioning | DVC |
| Data Storage | Azure Data Lake Storage |
| Batch Inference | Azure ML Batch Endpoints |
| Serving App | FastAPI + Uvicorn |
| Containerisation | Docker + Azure Container Registry |
| Deployment | Azure Container Apps |
| Drift Monitoring | Evidently |
| CI/CD | GitHub Actions |
| Infrastructure as Code | Terraform |
| Metrics | Prometheus + Grafana |
| Environment | Conda (managed by Azure ML) |

---

## Project Structure

```
mlops-with-github-and-azureml/
├── .azureml/
│   └── config.json                  # Azure ML workspace config
├── .dvc/
│   └── config                       # DVC remote storage config
├── .github/
│   └── workflows/
│       ├── train_model_dev.yml      # Trigger Azure ML training pipeline (dev)
│       ├── train_model_prod.yml     # Trigger Azure ML training pipeline (prod)
│       ├── score_model_dev.yml      # Run batch scoring (dev)
│       ├── score_model_prod.yml     # Run batch scoring (prod)
│       ├── build_push_app.yml       # Build & push Docker image to ACR, Deploy to Container Apps
│       └── monitor_drift.yml        # Weekly scheduled drift monitoring
├── app/
│   ├── main.py                      # FastAPI app — routes only
│   ├── model.py                     # Model loading from AML registry
│   ├── storage.py                   # Azure Blob Storage — prediction logging
│   ├── logger.py                    # Structured JSON logging
│   ├── auth.py                      # JWT authentication (optional)
│   ├── config.py                    # App configuration
│   ├── requirements.txt
│   ├── requirements-test.txt
│   └── tests/
│       ├── sample.csv               # Sample data for tests
│       └── test_main.py
├── monitoring/
│   ├── drift_monitor.py             # Evidently data drift report
│   └── requirements.txt
├── pipeline/
│   ├── config/                      # Azure ML component YAML definitions
│   │   ├── feature-engineering.yml
│   │   ├── feature-replace-missing-values.yml
│   │   ├── feature-selection.yml
│   │   ├── register-model.yml
│   │   ├── split-data.yml
│   │   └── train-model.yml
│   ├── scripts/                     # Pipeline step scripts
│   │   ├── conda.yaml               # Python environment specification
│   │   ├── feature_engineering.py
│   │   ├── feature_replace_missing_values.py
│   │   ├── feature_selection.py
│   │   ├── split_data.py
│   │   ├── train_model.py
│   │   ├── register_model.py
│   │   ├── score_model.py
│   │   ├── score_model_online.py
│   │   └── utils.py
│   ├── data.dvc                     # DVC-tracked data pointer (~128 MB)
│   ├── deploy-train.py              # Launch training pipeline
│   ├── deploy-score.py              # Deploy batch scoring endpoint
│   ├── redeploy.py                  # Rebuild Azure ML environment
│   └── requirements.txt
├── outputs/
│   └── drift_report.html            # Generated drift report (not tracked by git)
├── infra/
│   ├── environments/
│   │   ├── dev.tfvars               # Terraform variables for dev
│   │   ├── prod.tfvars              # Terraform variables for prod
│   │   ├── dev.backend.tfvars       # Terraform backend config for dev
│   │   └── prod.backend.tfvars      # Terraform backend config for prod
│   ├── main.tf                      # Resource groups
│   ├── ml.tf                        # AML workspace + dependencies
│   ├── storage.tf                   # Storage accounts + containers
│   ├── container.tf                 # ACR + Container App
│   ├── outputs.tf                   # Terraform outputs (ACR, AML, storage)
│   ├── variables.tf
│   ├── locals.tf
│   ├── providers.tf                 # Azure provider + remote backend
│   └── deploy.sh                    # Helper script: init + apply per environment
├── prometheus/
│   └── prometheus.yml               # Prometheus scrape config
├── docker-compose.yaml              # Local stack: app + Prometheus + Grafana
├── Dockerfile                       # Container image for the serving app
├── registered_model.dvc             # DVC-tracked model pointer
├── requirements-dev.txt             # Dev dependencies
└── setup/
    ├── credential_development.json
    └── credential_production.json
```

---

## Prerequisites

- Python 3.10+
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) with the ML extension (`az extension add -n ml`)
- An Azure subscription with:
  - An Azure ML Workspace
  - An Azure Data Lake Storage account (for DVC remote)
  - An Azure Container Registry (for Docker images)
  - An Azure Container Apps environment
- A GitHub repository with the required secrets configured (see [CI/CD Setup](#cicd-setup))

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/huyendt1610/mlops-with-github-and-azureml.git
cd mlops-with-github-and-azureml
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
cd pipeline
pip install -r requirements.txt
```

### 3. Configure Azure ML workspace

Update `.azureml/config.json` with your workspace details:

```json
{
    "subscription_id": "<your-subscription-id>",
    "resource_group": "<your-resource-group>",
    "workspace_name": "<your-aml-workspace-name>"
}
```

### 4. Authenticate with Azure

```bash
az login
az account set --subscription "<your-subscription-id>"
```

### 5. Configure DVC remote storage

```bash
dvc remote add -d myremote azure://<container>/data
dvc remote modify myremote account_name <your-storage-account>
# Add your SAS token to .dvc/config.local (not committed to git)
```

### 6. Pull data

```bash
dvc pull
```

---

## Running the Training Pipeline

### Option 1 — Run locally (deploys to Azure ML)

```bash
cd pipeline
python deploy-train.py
```

This will:
1. Create or reuse an Azure ML compute cluster
2. Register all pipeline components
3. Submit the pipeline as an Azure ML experiment (`aml_pipeline`)
4. Stream logs to the terminal

### Option 2 — Trigger via GitHub Actions

Push changes to the `dev` branch (or trigger manually in the Actions tab). The workflow fires automatically when any of these paths change:

- `pipeline/config/**`
- `pipeline/scripts/**`
- `pipeline/deploy-train.py`
- `pipeline/requirements.txt`

---

## Pipeline Steps

| Step | Script | Description |
|---|---|---|
| 1 | `feature_replace_missing_values.py` | Fill missing values in `Police_District` with 0 |
| 2 | `feature_engineering.py` | Extract year, time-of-day bins, plate origin, vehicle type |
| 3 | `feature_selection.py` | Drop irrelevant columns |
| 4 | `split_data.py` | 80/20 train/test split |
| 5 | `train_model.py` | Train Gradient Boosting Classifier; log metrics to MLflow |
| 6 | `register_model.py` | Register model in Azure ML Model Registry with metric tags |

---

## Serving App

The FastAPI app in `app/main.py` exposes two endpoints:

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/` | GET | None | Health check |
| `/predict` | POST | API Key | Accept a `.csv` file, return predictions + probabilities |

**Authentication:** all requests to `/predict` require an `X-API-Key` header:

```bash
curl -X POST https://your-app/predict \
  -H "X-API-Key: <your-api-key>" \
  -F "file=@data.csv"
```

Each prediction request is logged (input data + predictions + timestamp) to the `predictions-log` container in Azure Blob Storage for downstream drift monitoring. Structured JSON logs are written to stdout and collected by Azure Monitor.

### Run locally

Copy `.env.example` to `.env` and fill in the values, then:

```bash
pip install -r app/requirements.txt
export $(cat .env | xargs)
uvicorn app.main:app --reload
```

### Run with Docker

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

```bash
docker build -t chicagoticket-app .
docker run -p 8000:8000 --env-file .env chicagoticket-app
```

---

## Docker Image Versioning

Each image pushed to ACR carries three tags to link the image to both the git commit and the model version:

| Tag | Example | Meaning |
|---|---|---|
| `:<git-sha>` | `:c42284f` | Exact git commit |
| `:model-v<version>` | `:model-v5` | Model version from AML registry |
| `:latest` | `:latest` | Most recent build |

The model version is queried automatically from AML registry (`az ml model show --label latest`) during the CI build — no manual versioning required.

---

## Drift Monitoring

`monitoring/drift_monitor.py` compares live prediction data against the original training distribution using **Evidently**:

1. Reads all logged prediction inputs from the `predictions-log` blob container
2. Loads a 100k sample from the training CSV as reference data
3. Aligns columns present in both datasets
4. Runs a `DataDriftPreset` report and saves `outputs/drift_report.html`

```bash
pip install -r monitoring/requirements.txt
AZURE_STORAGE_ACCOUNT=<...> AZURE_STORAGE_ACCOUNT_KEY=<...> python monitoring/drift_monitor.py
```

---

## Batch Scoring Deployment

To deploy the trained model as a batch inference endpoint:

```bash
cd pipeline
python deploy-score.py
```

This creates the `ticket-endpoint` batch endpoint, deploys `ChicagoParkingTickets_model`, and runs a scoring job against the registered prediction dataset.

---

## Rebuilding the Azure ML Environment

If you update `pipeline/scripts/conda.yaml`, rebuild the managed environment:

```bash
cd pipeline
python redeploy.py
```

---

## Infrastructure Setup (Terraform)

All Azure resources are managed with Terraform in the `infra/` directory.

### Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/install) installed
- Azure CLI authenticated (`az login`)
- A storage account for Terraform remote state (created once manually):

```bash
az group create --name tfstate-rg --location norwayeast
az storage account create --name tfstatedevticketstorage --resource-group tfstate-rg --sku Standard_LRS
az storage container create --name tfstate --account-name tfstatedevticketstorage
```

### Deploy

```bash
cd infra
./deploy.sh dev    # deploy dev environment
./deploy.sh prod   # deploy prod environment
```

The script runs `terraform init` with the correct backend config then `terraform apply` with the matching tfvars.

### Resources created

| Resource | Purpose |
|---|---|
| Resource Group (`main`) | ACR, Container App, Storage |
| Resource Group (`aml`) | AML Workspace + dependencies |
| Azure Container Registry | Store Docker images |
| Azure Container App | Serve the FastAPI model API |
| Azure ML Workspace | Training, model registry |
| Azure Storage Account | Prediction logs, app data |

---

## Local Monitoring (Prometheus + Grafana)

Run the full local stack with Docker Compose:

```bash
docker compose up
```

| Service | URL |
|---|---|
| FastAPI app | http://localhost:8000 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 (admin/admin) |

Prometheus scrapes `/metrics` from the app automatically. Custom metrics tracked:
- `prediction_count` — number of predictions per label
- `prediction_rows` — number of rows per request

---

## CI/CD Setup

### Workflow: `train_model_dev.yml`

Triggers Azure ML training pipeline on changes to `pipeline/**`. Uses **OpenID Connect (OIDC)** for passwordless Azure authentication.

Secrets required (GitHub environment: `Development`):

| Secret | Description |
|---|---|
| `AZURE_CLIENT_ID` | Service principal / managed identity client ID |
| `AZURE_TENANT_ID` | Azure Active Directory tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |

### Workflow: `build_push_app.yml`

Triggers on changes to `app/**` or `Dockerfile`. Runs tests, builds and pushes the Docker image to ACR, then deploys to Azure Container Apps.

Secrets required (GitHub environment: `Production`):

| Secret | Description |
|---|---|
| `ACR_LOGIN_SERVER` | ACR login server (e.g. `myregistry.azurecr.io`) |
| `ACR_USERNAME` | ACR username |
| `ACR_PASSWORD` | ACR password |
| `ACR_NAME` | ACR name |
| `AZURE_CLIENT_ID` | Service principal client ID |
| `AZURE_TENANT_ID` | Azure Active Directory tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |
| `AZURE_STORAGE_ACCOUNT` | Storage account name |
| `AZURE_STORAGE_ACCOUNT_KEY` | Storage account key |
| `API_KEY` | API key for `/predict` endpoint authentication |

### Workflow: `deploy_infra.yml`

Triggers on changes to `infra/**` or manually via `workflow_dispatch`. Runs `terraform init` + `terraform apply` for the dev environment.

Secrets required (GitHub environment: `Production`):

| Secret | Description |
|---|---|
| `AZURE_CLIENT_ID` | Service principal client ID |
| `AZURE_TENANT_ID` | Azure Active Directory tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |

---

## Experiment Tracking

All training runs log the following metrics to **MLflow** (accessible via the Azure ML Studio UI):

- Accuracy
- F1 Score
- Precision
- Recall
- ROC-AUC

Navigate to **Azure ML Studio → Experiments → aml_pipeline** to compare runs.

---

## Data Versioning with DVC

Data files (~128 MB across 3 CSV files) are tracked by DVC and stored in Azure Blob Storage. The pointer file [pipeline/data.dvc](pipeline/data.dvc) is committed to git. Team members can reproduce the exact data version used for any commit with:

```bash
dvc pull
```

### Dataset Source

| File | Description |
|---|---|
| `pipeline/data/raw/ChicagoParkingTickets.csv` | Example/sample data for local development and testing |
