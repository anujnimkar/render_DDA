from pathlib import Path

from aws_cdk import (
    Duration,
    RemovalPolicy,
    Stack,
    aws_glue as glue,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_lambda_python_alpha as lambda_python,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_secretsmanager as secretsmanager,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
)
from constructs import Construct


class DdaPipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        repo_root = Path(__file__).resolve().parent.parent
        scripts_path = str(repo_root)
        config = self.node.try_get_context("pipeline") or {}

        bucket_name = config.get("bucket_name", "sf-fire-feeds")
        catalog_database = config.get("catalog_database", "sf_fire_db")
        raw_table = config.get("raw_table", "raw")
        curated_table = config.get("curated_table", "curated")
        curated_prefix = config.get("curated_prefix", "curated/")
        redshift_jdbc_url = config.get("redshift_jdbc_url", "")
        redshift_table = config.get("redshift_table", "public.fire_calls_redshift")
        redshift_temp_prefix = config.get("redshift_temp_prefix", "redshift-temp/")
        redshift_secret_arn = config.get("redshift_secret_arn", "")
        redshift_glue_connection_names = config.get("redshift_glue_connection_names", [])

        pipeline_bucket = s3.Bucket(
            self,
            "SfFireFeedsBucket",
            bucket_name=bucket_name,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            versioned=True,
            removal_policy=RemovalPolicy.RETAIN,
            auto_delete_objects=False,
        )

        script_deployment = s3deploy.BucketDeployment(
            self,
            "DeployGlueScripts",
            destination_bucket=pipeline_bucket,
            destination_key_prefix="scripts",
            sources=[
                s3deploy.Source.asset(
                    scripts_path,
                    exclude=[
                        ".git/*",
                        ".venv/*",
                        "__pycache__/*",
                        "cdk.out/*",
                        "cdk/*",
                    ],
                )
            ],
            prune=False,
            retain_on_delete=True,
        )

        ingest_lambda = lambda_python.PythonFunction(
            self,
            "SfFireIngestLambda",
            runtime=_lambda.Runtime.PYTHON_3_11,
            index="sf-fire-ingest-lambda.py",
            handler="lambda_handler",
            entry=scripts_path,
            timeout=Duration.minutes(5),
            memory_size=512,
        )
        ingest_lambda.add_environment("BUCKET_NAME", pipeline_bucket.bucket_name)
        pipeline_bucket.grant_read_write(ingest_lambda)

        glue_role = iam.Role(
            self,
            "SfFireGlueRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSGlueServiceRole"
                )
            ],
        )
        pipeline_bucket.grant_read_write(glue_role)

        glue_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "glue:GetDatabase",
                    "glue:GetDatabases",
                    "glue:GetTable",
                    "glue:GetTables",
                    "glue:GetPartition",
                    "glue:GetPartitions",
                    "glue:CreateTable",
                    "glue:UpdateTable",
                    "glue:BatchCreatePartition",
                    "glue:BatchDeletePartition",
                    "glue:BatchUpdatePartition",
                ],
                resources=["*"],
            )
        )
        glue_role.add_to_policy(
            iam.PolicyStatement(
                actions=["ec2:DescribeSubnets", "ec2:DescribeSecurityGroups", "ec2:DescribeVpcs"],
                resources=["*"],
            )
        )

        if redshift_secret_arn:
            redshift_secret = secretsmanager.Secret.from_secret_complete_arn(
                self,
                "ImportedRedshiftSecret",
                redshift_secret_arn,
            )
            redshift_secret.grant_read(glue_role)

        raw_to_curated_job = glue.CfnJob(
            self,
            "RawToCuratedJob",
            name="sf-fire-raw-to-curated",
            role=glue_role.role_arn,
            command=glue.CfnJob.JobCommandProperty(
                name="glueetl",
                script_location=(
                    f"s3://{pipeline_bucket.bucket_name}/scripts/"
                    "sf-fire-raw-to-curated.py"
                ),
                python_version="3",
            ),
            glue_version="4.0",
            max_retries=1,
            execution_property=glue.CfnJob.ExecutionPropertyProperty(max_concurrent_runs=1),
            default_arguments={
                "--job-language": "python",
                "--enable-metrics": "true",
                "--enable-continuous-cloudwatch-log": "true",
                "--TempDir": f"s3://{pipeline_bucket.bucket_name}/glue-temp/",
                "--catalog_database": catalog_database,
                "--raw_table": raw_table,
                "--curated_s3_path": f"s3://{pipeline_bucket.bucket_name}/{curated_prefix}",
            },
            number_of_workers=2,
            worker_type="G.1X",
        )
        raw_to_curated_job.node.add_dependency(script_deployment)

        athena_to_redshift_default_args = {
            "--job-language": "python",
            "--enable-metrics": "true",
            "--enable-continuous-cloudwatch-log": "true",
            "--TempDir": f"s3://{pipeline_bucket.bucket_name}/glue-temp/",
            "--catalog_database": catalog_database,
            "--curated_table": curated_table,
            "--redshift_jdbc_url": redshift_jdbc_url,
            "--redshift_table": redshift_table,
            "--redshift_temp_dir": f"s3://{pipeline_bucket.bucket_name}/{redshift_temp_prefix}",
        }
        if redshift_secret_arn:
            athena_to_redshift_default_args["--redshift_secret_arn"] = redshift_secret_arn

        athena_to_redshift_job = glue.CfnJob(
            self,
            "AthenaToRedshiftJob",
            name="sf-fire-athena-to-redshift",
            role=glue_role.role_arn,
            command=glue.CfnJob.JobCommandProperty(
                name="glueetl",
                script_location=(
                    f"s3://{pipeline_bucket.bucket_name}/scripts/"
                    "sf-fire-athena-to-redshift.py"
                ),
                python_version="3",
            ),
            glue_version="4.0",
            max_retries=1,
            execution_property=glue.CfnJob.ExecutionPropertyProperty(max_concurrent_runs=1),
            default_arguments=athena_to_redshift_default_args,
            connections=(
                glue.CfnJob.ConnectionsListProperty(
                    connections=redshift_glue_connection_names
                )
                if redshift_glue_connection_names
                else None
            ),
            number_of_workers=2,
            worker_type="G.1X",
        )
        athena_to_redshift_job.node.add_dependency(script_deployment)

        ingest_task = tasks.LambdaInvoke(
            self,
            "IngestRawData",
            lambda_function=ingest_lambda,
            output_path="$.Payload",
        )

        raw_to_curated_task = tasks.GlueStartJobRun(
            self,
            "RunRawToCurated",
            glue_job_name=raw_to_curated_job.ref,
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        athena_to_redshift_task = tasks.GlueStartJobRun(
            self,
            "RunAthenaToRedshift",
            glue_job_name=athena_to_redshift_job.ref,
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        sfn.StateMachine(
            self,
            "SfFirePipelineStateMachine",
            definition_body=sfn.DefinitionBody.from_chainable(
                ingest_task.next(raw_to_curated_task).next(athena_to_redshift_task)
            ),
            timeout=Duration.hours(2),
        )
