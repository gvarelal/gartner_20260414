#!/bin/bash
PROJECT_ID="demo4events10"
SA_EMAIL="53454032082-compute@developer.gserviceaccount.com"

echo "Granting Cloud Build Builder role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member=serviceAccount:$SA_EMAIL \
    --role=roles/cloudbuild.builds.builder

echo "Granting Artifact Registry Writer role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member=serviceAccount:$SA_EMAIL \
    --role=roles/artifactregistry.writer

echo "Granting Storage Object Admin role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member=serviceAccount:$SA_EMAIL \
    --role=roles/storage.objectAdmin

echo "Permissions updated. Please try the deployment again."
