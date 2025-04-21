# Pre-requisites

Install google-cloud-sdk

```
brew install google-cloud-sdk
```

# Authenticate

```
gcloud auth login
```

Follow instructions.

# Create project

```
gcloud projects create ai-receipt-vision-42sdf5x --name="AI Receipts"
gcloud config set ai-receipt-vision-42sdf5x
```

# Create App Engine app

```
gcloud app create --region=europe-west1
```
