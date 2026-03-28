import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read Athena curated table
athena_df = glueContext.create_dynamic_frame.from_catalog(
    database="sf_fire_db", 
    table_name="curated"
).toDF()

print(f"Athena records: {athena_df.count()}")

# Write to Redshift DIRECTLY (no JDBC connection needed)
athena_df.write \
    .format("com.databricks.spark.redshift") \
    .option("url", "jdbc:redshift://dda-rs-cluster.cfiyyszx8jiw.us-east-2.redshift.amazonaws.com:5439/sf_fire_db") \
    .option("dbtable", "public.fire_calls_redshift") \
    .option("tempdir", "s3://sf-fire-feeds/redshift-temp/") \
    .mode("overwrite") \
    .save()

job.commit()
print("✅ Athena → Redshift complete")
