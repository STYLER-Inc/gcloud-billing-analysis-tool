# GCP Billing Analysis Tool (for BigQuery)
This module is written to analyse Google Cloud Platform billing data
that has been exported to billing via the automatic export feature.

It returns data in dictionary format, which then may be used as is or,
for example, converted to JSON to serve other use cases.

# Running
You must specify the service account location if this is ran outside of
GCP, i.e. on your local machine.
```bash
$ PROJECT_ID="project-id" \
        DATA_SET="billing-dataset-name" \
        TABLE_NAME="table-name-in-dataset" \
        SLACK_API_TOKEN="your-slack-api-token" \
        GOOGLE_APPLICATION_CREDENTIALS="path-to-creds.json" \
        pipenv run python main.py
```
See `settings.py` for other settings.

## Coding

Run tests:

```shell script
pipenv run pytest --cov-report=html --cov=.
```

Before checking in, keep the code clean!

```shell script
pipenv run pylint **/*.py
```

## CI

The cloud build uses a community version cloud builder for [sonarqube](https://github.com/GoogleCloudPlatform/cloud-builders-community/tree/master/sonarqube) which must hav been built in the project running the cloud build before run.

It also needs to be built with version `4.2.0.1873` or later.

### Sonarcloud

In order to upload analysis results to Sonarcloud a secret key is required. You can update this secret key by running:

```shell script
echo -n $SECRET_KEY | gcloud kms encrypt \
  --plaintext-file=- \  # - reads from stdin
  --ciphertext-file=- \  # - writes to stdout
  --location=global \
  --keyring=gcloud-billing-analysis-tool-build \
  --key=sonarcloudLogin | base64
```

Then copying the output base64 string into the cloudbuild file.
