"""A Google Cloud Python Pulumi program"""

import pulumi
import pulumi_gcp as gcp

import json

config = pulumi.Config()

# create custom vpc
vpc_network = gcp.compute.Network("dataflow-demo-env",
    auto_create_subnetworks=False,
    description="PoC VPC for dataflow SAP to BigQuery",
    mtu=1460)


# create custom vpc subnet
dataflow_subnet1 = gcp.compute.Subnetwork("dataflow-demo-subnet1",
    ip_cidr_range="10.0.0.0/24",
    region="us-central1",
    network=vpc_network.id)


# create firewall allow ingress iap traffic
default_firewall = gcp.compute.Firewall("allow-from-iap",
    network=vpc_network.name,
    allows=[
        gcp.compute.FirewallAllowArgs(
            protocol="tcp",
            ports=[
                "22",
            ],
        ),
    ],
    priority=500,
    source_ranges=["35.235.240.0/20"])


# create firewall allow dataflow mysql traffic
default_firewall = gcp.compute.Firewall("allow-from-dataflow-worker",
    network=vpc_network.name,
    allows=[
        gcp.compute.FirewallAllowArgs(
            protocol="tcp",
            ports=[
                "3306",
                "12345-12346"
            ],
        ),
    ],
    priority=500,
    source_ranges=["10.0.0.0/24"])


# cloudsql ip address
private_ip_address = gcp.compute.GlobalAddress("cloudsql-privateip",
    purpose="VPC_PEERING",
    address_type="INTERNAL",
    prefix_length=16,
    network=vpc_network.id)
# cloudsql private connector
private_vpc_connection = gcp.servicenetworking.Connection("privateVpcConnection",
    network=vpc_network.id,
    service="servicenetworking.googleapis.com",
    reserved_peering_ranges=[private_ip_address.name])

# create cloudsql 
instance = gcp.sql.DatabaseInstance("dataflow-soruce-database",
    region="us-central1",
    database_version="MYSQL_8_0",
    settings=gcp.sql.DatabaseInstanceSettingsArgs(
        tier="db-f1-micro",
        disk_autoresize=False,
        disk_size=10,
        disk_type="PD_HDD",
        availability_type="ZONAL",
        ip_configuration=gcp.sql.DatabaseInstanceSettingsIpConfigurationArgs(
            ipv4_enabled=False,
            private_network=vpc_network.id,
            enable_private_path_for_google_cloud_services=True,
        ),
        backup_configuration=gcp.sql.DatabaseInstanceSettingsBackupConfigurationArgs(
            binary_log_enabled=False,
            enabled=False,
            backup_retention_settings=gcp.sql.DatabaseInstanceSettingsBackupConfigurationBackupRetentionSettingsArgs(
                retained_backups=3,
            )
        )
    ),
    deletion_protection=False,
    opts=pulumi.ResourceOptions(
        depends_on=[private_vpc_connection])
        )

# create cloudsql user
dataflow_user = gcp.sql.User("dataflow",
    instance=instance.name,
    password=config.require_secret('dbPassword'),
    type="BUILT_IN")


# create destination BigQuery
BQ = gcp.bigquery.Dataset("dataflow_demo",
                          dataset_id="dataflow_demo",
                          location="us-central1")

with open("bigquery.json") as jsonfile:
    schema = json.dumps(json.load(jsonfile))

default_table = gcp.bigquery.Table("defaultTable",
    dataset_id=BQ.dataset_id,
    table_id="demo",
    deletion_protection=False,
    opts=pulumi.ResourceOptions(parent=BQ),
    schema=schema)


# create bucket import sql file
bucket = gcp.storage.Bucket('dataflow-demo-bucket',
                            location="us-central1")
bucketObject = gcp.storage.BucketObject(
    'demo.sql',
    bucket=bucket.name,
    source=pulumi.FileAsset('demo.sql')
)

pulumi.export("Cloud Storage Object Path", pulumi.Output.all(bucket.url, bucketObject.output_name) \
    .apply(lambda args: f"{args[0]}/{args[1]}"))

pulumi.export("Cloud SQL Name", pulumi.Output.format(instance.name))
pulumi.export("Cloud SQL IP", pulumi.Output.format(instance.private_ip_address))
pulumi.export("Cloud SQL user", pulumi.Output.format(dataflow_user.id))

pulumi.export("VPC", pulumi.Output.format(vpc_network.self_link))
pulumi.export("Subnet", pulumi.Output.format(dataflow_subnet1.self_link))

pulumi.export("BigQuery table", pulumi.Output.format(default_table.id))
