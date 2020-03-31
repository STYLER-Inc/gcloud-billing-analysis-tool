# GCP Billing Analysis Tool (G-BAT) (for BigQuery)

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
