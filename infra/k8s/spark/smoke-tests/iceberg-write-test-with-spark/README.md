# Spark + Iceberg + Nessie Data Lake Example

This directory contains a complete example of how to write data to Apache Iceberg tables using Spark on Kubernetes, with Nessie as the catalog and RustFS as the storage backend.

## Overview

This example demonstrates a modern data lake architecture using:
- **Apache Spark**: Distributed data processing engine running on Kubernetes
- **Apache Iceberg**: Open table format for huge analytic datasets
- **Project Nessie**: Git-like data catalog with versioning capabilities
- **RustFS**: S3-compatible object storage for data persistence
- **Kubernetes**: Container orchestration for scalable deployment

### What the Application Does

The application reads a CSV file (`Churn_Modelling.csv`) from RustFS's bronze bucket and:
1. Creates a Nessie namespace (`demo`) if it doesn't exist
2. Drops any existing `churn` table
3. Creates a new Iceberg table with the CSV schema
4. Writes the data to the Iceberg table using Nessie catalog
5. Reads back the data to verify the operation
6. Displays sample records from the table

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Spark Driver  │    │   Spark Exec 1  │    │   Spark Exec 2  │
│   (K8s Pod)     │    │   (K8s Pod)     │    │   (K8s Pod)     │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │     Nessie Catalog       │
                    │  (Git-like versioning)   │
                    └─────────────┬────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │      RustFS Storage       │
                    │   (S3-compatible API)     │
                    │  bronze/   warehouse/     │
                    └───────────────────────────┘
```

## Prerequisites

Before running this example, ensure you have the complete data platform stack running:

### Required Components

1. **Kubernetes Cluster**: With sufficient resources for Spark jobs
2. **Spark Operator**: Installed and configured (see `../../spark-operator/README.md`)
3. **RustFS**: Object storage with proper buckets (see `../../rustfs/README.md`)
4. **Nessie**: Data catalog service (see `../../nessie/README.md`)
5. **Service Account**: Proper RBAC permissions for Spark jobs

### Data Requirements

- **Source Data**: `Churn_Modelling.csv` uploaded to RustFS bronze bucket
- **Buckets**: Both `bronze` and `warehouse` buckets must exist in RustFS

### Resource Requirements

**Minimum cluster resources needed:**
- **CPU**: 4+ cores (1 driver + 2 executors)
- **Memory**: 3.5+ GB (512MB driver + 1GB × 2 executors)
- **Storage**: Persistent storage for Iceberg tables
- **Network**: Connectivity between Spark, Nessie, and RustFS services

## Project Structure

```
iceberg-write-test-with-spark/
├── Dockerfile                              # Container image definition
├── iceberg_nessie.py                       # Main PySpark application
├── README.md                               # This documentation
├── requirements.txt                        # Python dependencies
└── write_to_iceberg_sparkApplication.yaml  # Kubernetes SparkApplication manifest
```

## File Descriptions

### `iceberg_nessie.py`
The main PySpark application that:
- **Reads CSV data** from RustFS S3-compatible storage (`s3a://bronze/Churn_Modelling.csv`)
- **Creates Nessie namespace** for data organization (`nessie.demo`)
- **Manages table lifecycle** (drop existing, create new schema)
- **Writes to Iceberg format** using Nessie catalog for versioning
- **Validates the operation** by reading back and displaying data

### `Dockerfile`
Multi-stage Docker build that:
- Uses the official `spark:3.5.3-java17` base image
- Sets up proper permissions for Ivy cache and application directory
- Installs Python dependencies from `requirements.txt`
- Copies the PySpark application into the container

### `write_to_iceberg_sparkApplication.yaml`
Comprehensive Kubernetes SparkApplication manifest defining:
- **Iceberg Dependencies**: All required Iceberg and Nessie JAR packages
- **S3/RustFS Configuration**: Connection settings for object storage
- **Nessie Integration**: Catalog configuration for table versioning
- **Resource Allocation**: Optimized CPU/memory for data processing
- **Volume Mounts**: Ivy cache for dependency management

## Quick Start

### Step 1: Verify Infrastructure

```bash
# Check if all required services are running
kubectl get pods -n spark-operator
kubectl get pods -n rustfs  
kubectl get pods -n nessie

# Verify service account exists
kubectl get serviceaccount spark
```

### Step 2: Prepare Source Data

Upload the `Churn_Modelling.csv` file to RustFS:

```bash
# Access RustFS Console at http://localhost:30903
# Create bronze bucket if needed:
kubectl run --rm -i aws-cli --image=amazon/aws-cli:latest --restart=Never \
  --env="AWS_ACCESS_KEY_ID=rustfsadmin" \
  --env="AWS_SECRET_ACCESS_KEY=rustfsadmin" \
  -- s3 mb s3://bronze --endpoint-url=http://rustfs-svc.rustfs.svc.cluster.local:9000

# Upload CSV file via RustFS console at http://localhost:30903
```

# Configure and upload


### Step 3: Build the Docker Image

```bash
# Navigate to the project directory
cd infra/k8s/spark/smoke-tests/iceberg-write-test-with-spark

# Build the container image
docker build -t spark-iceberg-nessie:1.0 .

# Verify the image was created
docker images | grep spark-iceberg-nessie
```

### Step 4: Submit the Spark Application

```bash
# Submit the application to Kubernetes
kubectl apply -f write_to_iceberg_sparkApplication.yaml

# Verify submission
kubectl get sparkapplications
```
- Wait for a while for being created dirver pod

### Step 5: Monitor the Application

```bash
# Check application status
kubectl get sparkapplications iceberg-nessie

# View all related pods
kubectl get pods -l spark-app-name=iceberg-nessie

# Follow driver logs in real-time
kubectl logs -f iceberg-nessie-driver

# Monitor Spark Operator logs
kubectl logs -f deployment/my-spark-operator-controller -n spark-operator

# Check executor logs
kubectl logs iceberg-nessie-exec-1
kubectl logs iceberg-nessie-exec-2
```

## Expected Output

When the application runs successfully, you should see output similar to:

```
24/12/18 10:15:23 INFO SparkContext: Running Spark version 3.5.3
24/12/18 10:15:24 INFO NessieClientBuilder: Creating Nessie client for URI: http://nessie.nessie.svc.cluster.local:19120/api/v2
24/12/18 10:15:25 INFO SparkSQLCLIDriver: Creating namespace nessie.demo
24/12/18 10:15:26 INFO SparkSQLCLIDriver: Dropping table nessie.demo.churn if exists
24/12/18 10:15:27 INFO IcebergTableUtil: Creating Iceberg table with schema
24/12/18 10:15:28 INFO SparkSQLCLIDriver: Writing data to nessie.demo.churn
24/12/18 10:15:30 INFO SparkSQLCLIDriver: Reading data back from table

+----------+--------+-----+--------+--------+-------+-------+-------+-------+--------+
|RowNumber |CustomerId|Surname|CreditScore|Geography|Gender|  Age|Tenure|Balance|NumOfProducts|
+----------+--------+-----+--------+--------+-------+-------+-------+-------+--------+
|        1 | 15634602|Hargrave|     619|   France| Female|   42|     2|    0.0|        1|
|        2 | 15647311|    Hill|     608|    Spain| Female|   41|     1|83807.86|        1|
|        3 | 15619304|    Onio|     502|   France| Female|   42|     8|159660.8|        3|
+----------+--------+-----+--------+--------+-------+-------+-------+-------+--------+
only showing top 3 rows

Application completed successfully!
```

## Check from trino
```sql
select * from iceberg.demo.churn c ;
```

## Iceberg Table Features

### Table Format Benefits

- **Schema Evolution**: Add, remove, or modify columns without rewriting data
- **Time Travel**: Query historical versions of your data
- **Partition Evolution**: Change partitioning strategy over time
- **ACID Transactions**: Guaranteed consistency across operations

### Nessie Catalog Benefits

- **Branching**: Create branches for development and testing
- **Merging**: Merge changes between branches like Git
- **Versioning**: Track all changes with commit history
- **Rollback**: Easily revert to previous states

## Configuration Details

### Iceberg Dependencies

The application includes these critical Maven packages:
```yaml
deps:
  packages:
    - "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.8.1"
    - "org.apache.iceberg:iceberg-spark-extensions-3.5_2.12:1.8.1"
    - "org.projectnessie.nessie-integrations:nessie-spark-extensions-3.5_2.12:0.102.5"
    - "org.apache.hadoop:hadoop-aws:3.3.4"
    - "org.apache.hadoop:hadoop-common:3.3.4"
```

### Spark Configuration

Key configuration settings for Iceberg + Nessie integration:
```yaml
sparkConf:
  # Nessie catalog configuration
  "spark.sql.catalog.nessie": "org.apache.iceberg.spark.SparkCatalog"
  "spark.sql.catalog.nessie.catalog-impl": "org.apache.iceberg.nessie.NessieCatalog"
  "spark.sql.catalog.nessie.uri": "http://nessie.nessie.svc.cluster.local:19120/api/v2"
  "spark.sql.catalog.nessie.warehouse": "s3a://warehouse/"
  
  # S3/RustFS configuration
  "spark.hadoop.fs.s3a.endpoint": "http://rustfs-svc.rustfs.svc.cluster.local:9000"
  "spark.hadoop.fs.s3a.access.key": "rustfsadmin"
  "spark.hadoop.fs.s3a.secret.key": "rustfsadmin"
  "spark.hadoop.fs.s3a.path.style.access": "true"
```

## Advanced Usage

### Querying with Time Travel

```python
# Query table as of specific timestamp
df_historical = spark.sql("""
    SELECT * FROM nessie.demo.churn 
    TIMESTAMP AS OF '2024-12-18 10:00:00'
""")

# Query table at specific snapshot
df_snapshot = spark.sql("""
    SELECT * FROM nessie.demo.churn 
    VERSION AS OF 'snapshot-id'
""")
```

### Schema Evolution Example

```python
# Add new column to existing table
spark.sql("""
    ALTER TABLE nessie.demo.churn 
    ADD COLUMN customer_segment STRING
""")

# Update schema and write new data
new_df.write.format("iceberg").mode("append").save("nessie.demo.churn")
```

### Nessie Branching

```python
# Create a new branch
spark.sql("CREATE BRANCH dev FROM main IN nessie")

# Switch to branch
spark.sql("USE nessie")
spark.sql("SET SESSION nessie.ref = 'dev'")

# Make changes on branch
spark.sql("CREATE TABLE nessie.demo.test_table ...")
```

## Troubleshooting

### Common Issues

**Application fails with dependency errors:**
```bash
# Check if Maven dependencies are downloading
kubectl logs iceberg-nessie-driver | grep -i "downloading"

# Verify Ivy cache permissions
kubectl exec iceberg-nessie-driver -- ls -la /tmp/.ivy2
```

**Cannot connect to Nessie:**
```bash
# Test Nessie connectivity
kubectl exec iceberg-nessie-driver -- curl http://nessie.nessie.svc.cluster.local:19120/api/v2

# Check Nessie service status
kubectl get svc -n nessie
kubectl get pods -n nessie
```

**S3/RustFS connection issues:**
```bash
# Test RustFS connectivity
kubectl exec iceberg-nessie-driver -- curl http://rustfs-svc.rustfs.svc.cluster.local:9000

# Verify RustFS credentials and buckets
kubectl run --rm -i s3-test --image=amazon/aws-cli:latest --restart=Never \
  --env="AWS_ACCESS_KEY_ID=rustfsadmin" \
  --env="AWS_SECRET_ACCESS_KEY=rustfsadmin" \
  -- s3 ls --endpoint-url=http://rustfs-svc.rustfs.svc.cluster.local:9000
```

**Table already exists errors:**
```bash
# Check existing tables in Nessie
curl http://localhost:30919/api/v2/trees/tree/main/entries

# Drop table manually if needed
kubectl exec iceberg-nessie-driver -- spark-sql \
  -e "DROP TABLE IF EXISTS nessie.demo.churn"
```

### Debugging Commands

```bash
# View detailed application status
kubectl describe sparkapplication iceberg-nessie

# Check all events in namespace
kubectl get events --sort-by='.lastTimestamp'

# Access Spark UI (if available)
kubectl port-forward iceberg-nessie-driver 4040:4040
# Visit http://localhost:4040

# Check Nessie UI
kubectl port-forward -n nessie svc/nessie 19120:19120
# Visit http://localhost:19120

# RustFS Console
kubectl port-forward -n rustfs svc/rustfs-console-nodeport 9001:9001
# Visit http://localhost:30903
```

### Performance Tuning

```yaml
# For larger datasets, increase resources:
driver:
  cores: 2
  memory: "1g"
executor:
  cores: 2
  instances: 4
  memory: "2g"

# Optimize S3 settings:
sparkConf:
  "spark.hadoop.fs.s3a.block.size": "134217728"  # 128MB
  "spark.hadoop.fs.s3a.multipart.size": "104857600"  # 100MB
  "spark.hadoop.fs.s3a.multipart.threshold": "2147483647"  # 2GB
```

## Cleanup

```bash
# Delete the SparkApplication (pods auto-cleanup in 10 minutes)
kubectl delete sparkapplication iceberg-nessie

# Verify cleanup
kubectl get pods -l spark-app-name=iceberg-nessie

# Remove Docker image (optional)
docker rmi spark-iceberg-nessie:1.0

# Clean up Iceberg table (optional)
curl -X DELETE http://localhost:30919/api/v2/trees/tree/main/entries/demo.churn
```

## Next Steps

After successfully running this example:

1. **Schema Evolution**: Experiment with adding/removing columns
2. **Time Travel Queries**: Practice querying historical data
3. **Nessie Branching**: Try development workflows with branches
4. **Performance Optimization**: Tune for larger datasets
5. **Production Deployment**: Add monitoring, security, and CI/CD
6. **Data Quality**: Implement validation and testing frameworks

## Related Documentation

- [Simple Spark Application](../submit-simple-sparkapp/README.md)
- [Spark Operator Installation](../../spark-operator/README.md  )
- [RustFS Setup](../../../rustfs/README.md)
- [Nessie Configuration](../../../nessie/README.md)
- [Apache Iceberg Documentation](https://iceberg.apache.org/docs/latest/)
- [Project Nessie Documentation](https://projectnessie.org/guides/)
- [Spark SQL Guide](https://spark.apache.org/docs/latest/sql-programming-guide.html)
