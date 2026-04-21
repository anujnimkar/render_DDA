import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import *
from pyspark.sql.types import *

required_args = ["JOB_NAME"]
optional_args = [
    "catalog_database",
    "raw_table",
    "curated_s3_path",
]

present_optional = [
    arg_name
    for arg_name in optional_args
    if f"--{arg_name}" in sys.argv
]

args = getResolvedOptions(sys.argv, required_args + present_optional)

catalog_database = args.get("catalog_database", "sf_fire_db")
raw_table = args.get("raw_table", "raw")
curated_s3_path = args.get("curated_s3_path", "s3://sf-fire-feeds/curated/")
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read raw data
raw_df = glueContext.create_dynamic_frame.from_catalog(
    database=catalog_database,
    table_name=raw_table
).toDF()

print(f"Raw records: {raw_df.count()}")

# DEBUG: Show samples
print("=== DEBUG: received_dttm samples ===")
raw_df.select("received_dttm").distinct().show(20, truncate=False)
raw_df.select("received_dttm").filter(col("received_dttm").isNotNull()).show(5, truncate=False)

# FIXED: Parse ISO 8601 "2026-02-01T00:03:11.000" format
def parse_fire_timestamp(ts_col):
    # Primary: ISO 8601 yyyy-MM-ddTHH:mm:ss.SSS
    parsed = to_timestamp(col(ts_col), "yyyy-MM-dd'T'HH:mm:ss.SSS")
    
    # Fallbacks (if needed)
    parsed = coalesce(
        parsed,
        to_timestamp(col(ts_col), "yyyy-MM-dd'T'HH:mm:ss"),  # No millis
        lit(None).cast("timestamp")
    )
    
    return parsed

# Transform
curated_df = (raw_df
    .filter(col("call_number").isNotNull())
    .dropDuplicates(["call_number"])
    .withColumn("received_ts", parse_fire_timestamp("received_dttm"))
    .withColumn("year", year(col("received_ts")))
    .withColumn("month", month(col("received_ts")))
    .withColumn("day", dayofmonth(col("received_ts")))
    .select(
        "call_number", "received_ts", "call_type", 
        "city", "station_area", "address", "case_location", "zipcode_of_incident", 
        "year", "month", "day"
    )
    .filter(col("received_ts").isNotNull())  # Remove parse failures
)

print(f"Curated records: {curated_df.count()}")

# DEBUG: Verify parsing works
print("=== DEBUG: Parsed timestamps ===")
curated_df.select("received_ts", "year", "month", "day") \
    .filter(col("received_ts").isNotNull()).show(10, truncate=False)

# Write partitioned Parquet
curated_df.write \
    .mode("overwrite") \
    .partitionBy("year", "month", "day") \
    .parquet(curated_s3_path)

job.commit()
print("✅ ETL complete: ISO 8601 timestamps partitioned correctly")
