# MLOps with GitHub and Azure ML

An end-to-end MLOps project demonstrating how to build, train, deploy, and manage a machine learning model using **Azure Machine Learning**, **GitHub Actions**, and **DVC**. The model predicts whether a Chicago parking ticket will be paid or remain outstanding.

---

## Architecture Overview

```
GitHub Actions (CI/CD)
       │
       ▼
Azure ML Pipeline
  ├── Replace Missing Values
  ├── Feature Engineering
  ├── Feature Selection
  ├── Split Data
  ├── Train Model  ──► MLflow (metrics + model)
  └── Register Model ──► Azure ML Model Registry
                                │
                                ▼
                    Azure ML Batch Endpoint
                    (ticket-endpoint)
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
| CI/CD | GitHub Actions |
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
│       └── train_model_dev.yml      # CI/CD pipeline
├── notebooks/
│   ├── chicago_ticket.ipynb         # Data exploration
│   ├── azureml-in-a-day.ipynb       # Azure ML concepts
│   ├── mlflow_dagshub.ipynb         # MLflow experiment tracking
│   ├── data_engineer.ipynb          # Data engineering
│   └── check.ipynb                  # Validation
├── pipeline/
│   ├── config/                      # Azure ML component YAML definitions
│   │   ├── feature-engineering.yml
│   │   ├── feature-replace-missing-values.yml
│   │   ├── feature-selection.yml
│   │   ├── register-model.yml
│   │   ├── split-data.yml
│   │   └── train-model.yml
│   ├── environment/
│   │   └── conda.yaml               # Python environment specification
│   ├── scripts/                     # Pipeline step scripts
│   │   ├── feature_engineering.py
│   │   ├── feature_replace_missing_values.py
│   │   ├── feature_selection.py
│   │   ├── split_data.py
│   │   ├── train_model.py
│   │   ├── register_model.py
│   │   ├── score_model.py
│   │   └── utils.py
│   ├── data.dvc                     # DVC-tracked data pointer (~128 MB)
│   ├── deploy-train.py              # Launch training pipeline
│   ├── deploy-score.py              # Deploy batch scoring endpoint
│   ├── redeploy.py                  # Rebuild Azure ML environment
│   └── requirements.txt
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
- `pipeline/environment/**`
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
| 4 | `split_data.py` | 80/20 train/test split on first 100k records |
| 5 | `train_model.py` | Train Gradient Boosting Classifier; log metrics to MLflow |
| 6 | `register_model.py` | Register model in Azure ML Model Registry with metric tags |

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

If you update `pipeline/environment/conda.yaml`, rebuild the managed environment:

```bash
cd pipeline
python redeploy.py
```

---

## CI/CD Setup

The workflow in [.github/workflows/train_model_dev.yml](.github/workflows/train_model_dev.yml) uses **OpenID Connect (OIDC)** for passwordless Azure authentication.

Add the following secrets to your GitHub repository under **Settings → Secrets → Actions** (in the `Development` environment):

| Secret | Description |
|---|---|
| `AZURE_CLIENT_ID` | Service principal / managed identity client ID |
| `AZURE_TENANT_ID` | Azure Active Directory tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |

> The workflow also dynamically writes `.azureml/config.json` from these secrets, so no static workspace config needs to be stored in the repo.

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

---

## Notebooks

| Notebook | Purpose |
|---|---|
| `chicago_ticket.ipynb` | Initial data exploration and EDA |
| `azureml-in-a-day.ipynb` | Azure ML SDK concepts walkthrough |
| `mlflow_dagshub.ipynb` | MLflow experiment tracking demo |
| `check.ipynb` | Validation and sanity checks |
