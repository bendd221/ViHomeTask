# 📈 Stock Analytics Platform (AWS CDK + FastAPI)

Overview
==========================

This project provisions a scalable analytics platform on AWS using AWS CDK.
It consists of two main stacks:

  - Data Pipeline Stack
      Provisions AWS Glue jobs responsible for ingesting and transforming stock market data.

  - API Stack
      Provisions an API backed by FastAPI, exposing processed analytics data to consumers.

The infrastructure is defined using AWS CDK, while the API application logic lives separately.

--------------------------
Architecture
--------------------------

High-level flow:

  1. Stocks data pipeline is generated through the CDK to create either one or multiple glue jobs (depends on the requirements)
  2. A simple API with four endpoints (healths + three metrics) is generated through a different CDK stack.
  3. Tables in AWS Data Catalog are currently created manually, but can also be generated using a Crawler or Partition Projection (Hopefully I got to implementing it)
  4. Then after the glue jobs are finished,the API is used to query Athena return data to the consumer.

Project structure:

    .
    ├── api/
    │   └── app/
    │       ├── routers/          # FastAPI route definitions (health + metrics)
    │       ├── services/         # Currently, only AthenaService to abstract some of the logic
    │       ├── __init__.py
    │       ├── config.py         # FastAPI and AWS Config data.
    │       ├── main.py           # FastAPI entry point
    │       ├── Dockerfile        # API container definition (Python 3.9)
    │       └── requirements.txt  # API dependencies
    │
    ├── aws_cdk/
    │   ├── common/               # Shared CDK constructs/utilities, mainly props of each stack and a config mapper.
    │   ├── stock_analytics_api/
    │   │   └── api_infrastructure.py
    │   │       # CDK stack for the API (ECS using L3 FarGateService + S3 Permissions)
    │   └── stock_analytics_data_pipeline/
    │       ├── infrastructure/   # Glue jobs, roles, S3, etc.
    │       ├── local_source_data/# Sample/local input data
    │       └── runtime/          # Glue job scripts
    │
    ├── app.py                    # CDK app entry point
    ├── cdk.json                  # CDK configuration
    ├── README.md # hi
    └── .gitignore

--------------------------
Stacks
--------------------------

1. Data Pipeline Stack

Purpose:

  - Dynamically provision AWS Glue jobs
  - Manage IAM roles and permissions
  - Define data storage layout (e.g. S3 prefixes, bucket creation)

Location:
  aws_cdk/stock_analytics_data_pipeline/

2. API Stack

Purpose:

  - Deploy infrastructure required to run the API
  - Grant permissions to the API for athena data access

Location:
  aws_cdk/stock_analytics_api/

--------------------------
FastAPI Application
--------------------------

The API implementation lives outside the CDK stacks and is deployed as an application through ApiStack.

Location:
  api/app/

--------------------------
Deployment
--------------------------

Prerequisites:

  - Python 3.9+
  - AWS CLI configured
  - AWS CDK installed
  - Docker (for API container builds)

Install dependencies:

  pip install -r api/app/requirements.txt #For the application itself

  pip install -r aws_cdk/requirements.txt #For the CDK Scripts

Bootstrap CDK (once per account/region):

  cdk bootstrap

Deploy stacks

Deploy both stacks:

  cdk deploy --all

Or deploy individually:

  cdk deploy StockAnalyticsDataPipelineStack

  cdk deploy StockAnalyticsApiStack

cdk.json includes an aws profile spec, can remove it if your keys are stored in the default profile, otherwise, don't forget to change the profile name.
can also use aws configure `--profile <PROFILENAME>` to create a new profile, if needed.

Example cdk.json:
{
  "app": "py app.py",
  "profile": "vi"
}
--------------------------
Local Development
--------------------------

Run FastAPI locally:

  cd api/app

  uvicorn main:app --reload

- Java SDK 17+ for PySpark 4.0.1 or else the session creation hangs
--------------------------
Configuration
--------------------------

  CDK props are defined through app.py, and can be moved to environment variables if needed (Please make sure to not use any inside the Stacks/Constructs themselves and only pass them through the highest layer app.py)

  api/app/config.py is what the API needs to function, can use python-dotenv and a .env file to locally work and imitate env variables.

--------------------------
Usage
--------------------------

After deploying the CDK, you should see the following message with the load balancer's endpoint:

  Outputs:

  ```
  StockAnalyticsAPIStack.LoadBalancerDNS = StockA-Stock-myexample-test.eu-central-1.elb.amazonaws.com
  StockAnalyticsAPIStack.StocksAnalyticsApiLoadBalancerDNSF698D36A = StockA-Stock-myexample-test.eu-central-1.elb.amazonaws.com
  StockAnalyticsAPIStack.StocksAnalyticsApiServiceURL6F11E8A2 = http://StockA-Stock-myexample-test.eu-central-1.elb.amazonaws.com
  Stack ARN:
  arn:aws:cloudformation:eu-central-1:myaccount:stack/StockAnalyticsAPIStack/irrelevnant
  ```

Use the DNS to send api requests for data:

```python
  import requests
  results = requests.get(http://StockA-Stock-myexample-test.eu-central-1.elb.amazonaws.com/metrics/most-valuable-day)
  results.content
  #or whatever you want to do
```
Available endpoints:

  /most-valueble-day

  /most-volatile

  /average-daily-return?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD 

  /health

--------------------------
Notes
--------------------------

  - Infrastructure and application code are intentionally separated.
  - Glue jobs are currently split into three but the I/O Concern is something I had in mind, so one glue job that does all three might be the correct approach depending on the demand (Time, Scalability, Organization etc)
  - Schemas are currently being defined through the script of each glue job, but we can use partition projection to pre-determine the tables to keep it clear in the CDK.
  - I used Hive tables, but with a bit of code modification to the scripts and a different parameter, we can easily change to an Iceberg table
  - Annualize Volatility is one of the column names, but the task itself required data from all years, was this a mistake?
  - AWS Lambda was a consideration at first (for the API) but I have decided to go with ECS as Lambda has a 15 minutes response timeout, and if the data scales more it might become a problem at one point.
  - One of the results have a single line it in, and Athena has a minimum pay-per-request of 10MB, so even a single byte of result will charge for the full 10MB, maybe there's a better solution to that?

--------------------------
Future Improvements
--------------------------

  - Tests (Didn't have time and would rather not just blindly generate them with AI)
  - Improve observability (logs, metrics are lacking here)
  - Error handling
  - Boilerplate code of glue job scripts into a separate module (--additional-python-modules)
