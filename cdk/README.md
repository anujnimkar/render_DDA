# SF Fire Data Pipeline CDK

This CDK app provisions infrastructure for the three pipeline scripts:

- `sf-fire-ingest-lambda.py` (AWS Lambda ingest)
- `sf-fire-raw-to-curated.py` (AWS Glue job)
- `sf-fire-athena-to-redshift.py` (AWS Glue job)

It creates:

- an S3 bucket for pipeline data and script artifacts
- one Lambda function for ingestion
- two AWS Glue jobs
- one Step Functions state machine that runs:
  1) ingest lambda
  2) raw-to-curated glue job
  3) athena-to-redshift glue job

## Deploy

From the repo root:

```bash
cd cdk
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cdk bootstrap aws://<account-id>/<region>
cdk synth -c account=<account-id> -c region=<region>
cdk deploy -c account=<account-id> -c region=<region>
```

## Configure Account-Specific Values

Edit `cdk/cdk.json` under `context.pipeline` before deployment:

- `bucket_name`: global S3 bucket name to create in your account
- `catalog_database`: Glue Data Catalog database name
- `raw_table`: raw table name in Glue Data Catalog
- `curated_table`: curated table name in Glue Data Catalog
- `curated_prefix`: curated parquet prefix inside the bucket
- `redshift_jdbc_url`: JDBC URL for your Redshift cluster and database
- `redshift_table`: target Redshift table
- `redshift_temp_prefix`: temp S3 prefix for Redshift loads
- `redshift_secret_arn`: Secrets Manager ARN containing Redshift credentials (`username`, `password`)
- `redshift_glue_connection_names`: one or more existing Glue connection names for private/VPC Redshift access

Example:

```json
"pipeline": {
  "bucket_name": "my-sf-fire-feeds-prod",
  "catalog_database": "sf_fire_db",
  "raw_table": "raw",
  "curated_table": "curated",
  "curated_prefix": "curated/",
  "redshift_jdbc_url": "jdbc:redshift://my-cluster.xxxxxx.us-east-2.redshift.amazonaws.com:5439/sf_fire_db",
  "redshift_table": "public.fire_calls_redshift",
  "redshift_temp_prefix": "redshift-temp/",
  "redshift_secret_arn": "arn:aws:secretsmanager:us-east-2:123456789012:secret:my-redshift-credentials",
  "redshift_glue_connection_names": [
    "my-redshift-vpc-connection"
  ]
}
```

## Notes

- Script runtime values are parameterized and passed from CDK context.
- Glue script locations are uploaded to S3 under `scripts/`.
- If `redshift_secret_arn` is set, CDK grants Glue role read access and the job reads `username/password` from that secret.
- If Redshift is private, create a Glue connection for your VPC/subnet/security groups and set its name in `redshift_glue_connection_names`.
