# GCP Billing Analysis Tool (G-BAT) (for BigQuery)
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
        pipenv run python g-bat.py
```
See `settings.py` for other settings.
