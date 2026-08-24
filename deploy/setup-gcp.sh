#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${1:?Usage: ./setup-gcp.sh PROJECT_ID [REGION]}"
REGION="${2:-asia-southeast1}"
SERVICE="fastapi-firebase-api"
REPOSITORY="apps"
SA_NAME="fastapi-firebase-api"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# Enable required APIs.
gcloud config set project "$PROJECT_ID"
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  firebase.googleapis.com \
  firestore.googleapis.com \
  identitytoolkit.googleapis.com

# Artifact Registry repository.
gcloud artifacts repositories create "$REPOSITORY" \
  --repository-format=docker \
  --location="$REGION" \
  --description="Application container images" 2>/dev/null || true

# Runtime service account.
gcloud iam service-accounts create "$SA_NAME" \
  --display-name="FastAPI Firebase Cloud Run runtime" 2>/dev/null || true

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/datastore.user"

echo "Runtime service account: $SA_EMAIL"
echo "Next: create a Firebase project/application in the Firebase console, enable Authentication providers, and initialize Firestore."
