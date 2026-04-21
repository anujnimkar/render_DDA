import sys
import json
import boto3
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

required_args = ["JOB_NAME"]
optional_args = [
    "catalog_database",
    "curated_table",
    "redshift_jdbc_url",
    "redshift_table",
    "redshift_temp_dir",
    "redshift_secret_arn",
]

present_optional = [
    arg_name
    for arg_name in optional_args
    if f"--{arg_name}" in sys.argv
]

args = getResolvedOptions(sys.argv, required_args + present_optional)

catalog_database = args.get("catalog_database", "sf_fire_db")
curated_table = args.get("curated_table", "curated")
redshift_jdbc_url = args.get(
    "redshift_jdbc_url",
    "jdbc:redshift://dda-rs-cluster.cfiyyszx8jiw.us-east-2.redshift.amazonaws.com:5439/sf_fire_db",
)
redshift_table = args.get("redshift_table", "public.fire_calls_redshift")
redshift_temp_dir = args.get("redshift_temp_dir", "s3://sf-fire-feeds/redshift-temp/")
redshift_secret_arn = args.get("redshift_secret_arn")
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read Athena curated table
athena_df = glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database,
    table_name=curated_table
).toDF()

print(f"Athena records: {athena_df.count()}")

redshift_write = (
    athena_df.write
    .format("com.databricks.spark.redshift")
    .option("url", redshift_jdbc_url)
    .option("dbtable", redshift_table)
    .option("tempdir", redshift_temp_dir)
)

if redshift_secret_arn:
    secrets_client = boto3.client("secretsmanager")
    secret_value = secrets_client.get_secret_value(SecretId=redshift_secret_arn)
    secret_payload = secret_value.get("SecretString", "{}")
    credentials = json.loads(secret_payload)
    redshift_user = credentials.get("username")
    redshift_password = credentials.get("password")
    if not redshift_user or not redshift_password:
        raise ValueError(
            "Redshift secret must include 'username' and 'password' keys."
        )
    redshift_write = (
        redshift_write.option("user", redshift_user)
        .option("password", redshift_password)
    )

# Write to Redshift DIRECTLY (no JDBC connection needed)
redshift_write.mode("overwrite").save()

job.commit()
print("✅ Athena → Redshift complete")
