# Dataflow Test Environment

以下範例為建置供 [Google Cloud Dataflow](https://cloud.google.com/dataflow) template [JDBC to BigQuery](https://cloud.google.com/dataflow/docs/guides/templates/provided/jdbc-to-bigquery) 的前置架構建置，主要目的是供測試 Column Schema 內有 BigQuery 不接受的特殊字元時，利用 
1. Alias 
2. custom template 進行解決

環境包含
- VPC
- Cloud SQL (MySQL)
- BigQuery

MySQL demo.sql 的 database 為 test，主要用來測試的 table 為 demo

## Prerequisites

Ensure you have [Python 3](https://www.python.org/downloads/) and [the Pulumi CLI](https://www.pulumi.com/docs/get-started/install/).

We will be deploying to Google Cloud Platform (GCP), so you will need an account. If you don't have an account,
[sign up for free here](https://cloud.google.com/free/). In either case,
[follow the instructions here](https://www.pulumi.com/docs/intro/cloud-providers/gcp/setup/) to connect Pulumi to your GCP account.

This example assumes that you have GCP's `gcloud` CLI on your path. This is installed as part of the
[GCP SDK](https://cloud.google.com/sdk/).

## Running the Example

After cloning this repo, `cd` into it and run these commands. 

1. Create a new stack, which is an isolated deployment target for this example:

    ```bash
    $ pulumi stack init dev
    ```

2. Set the required configuration variables for this program:

    ```bash
    $ pulumi config set gcp:project [your-gcp-project-here]
    $ pulumi config set --secret dbPassword [your-database-password-here]
    ```

   This shows how stacks can be configurable in useful ways. You can even change these after provisioning.

3. Deploy everything with the `pulumi up` command.

    ```bash
    $ pulumi up
    ```


4. Import a SQL dump file to Cloud SQL for MySQL

> Notice may have BUG -> ERROR: (gcloud.sql.import.sql) HTTPError 403: The service account does not have the required permissions for the bucket. Try use Console. For more detail about import a SQL dump file to Cloud SQL for MySQL, see the [informaimport a SQL dump file to Cloud SQL for MySQtion](https://cloud.google.com/sql/docs/mysql/import-export/import-export-sql#import_a_sql_dump_file_to)

    ```
    $ gcloud sql import sql [your-database-name] [gs://bucket-name/sql-file]
    ```

5. Create Dataflow use JDBC to BigQuery

6. Once you are done, you can destroy all of the resources, and the stack:

    ```bash
    $ pulumi destroy
    $ pulumi stack rm
    ```
