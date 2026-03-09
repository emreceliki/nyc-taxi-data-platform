# Simple Spark Application on Kubernetes

This directory contains a basic example of how to submit and run a PySpark application on Kubernetes using the Spark Operator.

## Overview

This example demonstrates:
- **Containerized Spark Application**: A simple PySpark job packaged in a Docker container
- **Kubernetes Deployment**: Using SparkApplication CRD to submit jobs to Kubernetes
- **Cluster Mode Execution**: Running Spark driver and executors as Kubernetes pods
- **Basic Data Processing**: Creating a DataFrame with 1 million rows and performing simple transformations

The application creates a DataFrame with sequential IDs from 0 to 999,999, adds two calculated columns (`plus_10` and `plus_20`), and displays basic statistics and sample data.

## Prerequisites

Before running this example, ensure you have:

1. **Kubernetes Cluster**: A running Kubernetes cluster with sufficient resources
2. **Spark Operator**: Installed and configured (see `../spark-operator/README.md`)
3. **Service Account**: Proper RBAC permissions for Spark jobs
4. **Docker**: For building the application image
5. **kubectl**: Configured to access your cluster

## Project Structure

```
submit-simple-sparkapp/
├── Dockerfile              # Container image definition
├── README.md               # This documentation
├── requirements.txt        # Python dependencies
├── spark_on_k8s_app.py     # Main PySpark application
└── sparkApplication.yaml   # Kubernetes SparkApplication manifest
```

## File Descriptions

### `spark_on_k8s_app.py`
The main PySpark application that:
- Creates a SparkSession with the name "Spark on K8s"
- Generates a DataFrame with 1,000,000 sequential numbers
- Adds two computed columns (`plus_10` and `plus_20`)
- Prints the row count, schema, and first 100 rows
- Includes a 30-second sleep for observation
- Gracefully shuts down the Spark context

### `Dockerfile`
- Uses the official `spark:3.5.3-java17` base image
- Sets up the working directory at `/app`
- Installs Python dependencies from `requirements.txt`
- Copies the PySpark application into the container

### `sparkApplication.yaml`
Kubernetes SparkApplication manifest defining:
- **Application Type**: Python with version 3
- **Execution Mode**: Cluster mode (driver runs in Kubernetes)
- **Resource Allocation**: 1 driver + 2 executors with specified CPU/memory
- **Restart Policy**: Automatic retry on failures
- **Service Account**: Uses the `spark` service account for RBAC

## Quick Start

### Step 1: Verify Prerequisites

```bash
# Check if Spark Operator is running
kubectl get pods -n spark-operator

# Verify service account exists
kubectl get serviceaccount spark
```

### Step 2: Build the Docker Image

```bash
# Build the container image
docker build -t spark-k8s-app:2.0 .

# Verify the image was created
docker images | grep spark-k8s-app
```

**Note**: In a real Kubernetes cluster, you would need to push this image to a container registry accessible by your cluster (Docker Hub, ECR, GCR, etc.).

### Step 3: Submit the Spark Application

```bash
# Submit the application to Kubernetes
kubectl apply -f sparkApplication.yaml

# Verify submission
kubectl get sparkapplications
```

### Step 4: Monitor the Application

```bash
# Check application status
kubectl get sparkapplications pyspark-on-k8s

# View all related pods
kubectl get pods -l spark-app-name=pyspark-on-k8s

# Follow driver logs in real-time
kubectl logs -f pyspark-on-k8s-driver

# Check executor logs (replace with actual pod name)
kubectl logs pyspark-on-k8s-exec-1
kubectl logs pyspark-on-k8s-exec-2
```

## Expected Output

When the application runs successfully, you should see output similar to:

```
*******************************
1000000
root
 |-- id: long (nullable = false)
 |-- plus_10: long (nullable = false)
 |-- plus_20: long (nullable = false)

+------+-------+-------+
|    id|plus_10|plus_20|
+------+-------+-------+
|     0|     10|     20|
|     1|     11|     21|
|     2|     12|     22|
|     3|     13|     23|
|     4|     14|     24|
|   ...|    ...|    ...|
+------+-------+-------+
only showing top 100 rows

Spark is shutting down.
```

## Application Lifecycle

1. **Submission**: Spark Operator creates driver pod
2. **Initialization**: Driver pod starts and initializes SparkSession
3. **Resource Allocation**: Kubernetes creates 2 executor pods
4. **Execution**: Data processing occurs across driver and executors
5. **Completion**: Application completes, pods are cleaned up
6. **Cleanup**: SparkApplication remains for status/history

## Resource Configuration

The current configuration allocates:

| Component | CPU Cores | CPU Limit | Memory | Instances |
|-----------|-----------|-----------|---------|-----------|
| Driver    | 1         | 1.2       | 512MB   | 1         |
| Executor  | 1         | -         | 1.5GB   | 2         |
| **Total** | **3**     | **-**     | **3.5GB** | **3**   |

### Adjusting Resources

To modify resource allocation, edit `sparkApplication.yaml`:

```yaml
# For smaller environments
driver:
  cores: 1
  memory: "256m"
executor:
  cores: 1
  instances: 1
  memory: "512m"

# For larger datasets
driver:
  cores: 2
  memory: "1g"
executor:
  cores: 2
  instances: 4
  memory: "2g"
```

## Troubleshooting

### Common Issues

**Application stays in `PENDING` state:**
```bash
# Check pod events
kubectl describe pod pyspark-on-k8s-driver

# Common causes:
# - Insufficient cluster resources
# - Image pull failures
# - Service account permissions
```

**Image pull errors:**
```bash
# For local development, ensure image exists locally on all nodes
# For production, push to a registry:
docker tag spark-k8s-app:2.0 your-registry/spark-k8s-app:2.0
docker push your-registry/spark-k8s-app:2.0

# Update sparkApplication.yaml with registry URL
```

**Permission denied errors:**
```bash
# Verify service account and RBAC
kubectl describe serviceaccount spark
kubectl describe clusterrolebinding spark-role

# If missing, create them:
kubectl create serviceaccount spark
kubectl create clusterrolebinding spark-role \
  --clusterrole=edit \
  --serviceaccount=default:spark
```

### Debugging Commands

```bash
# View detailed application status
kubectl describe sparkapplication pyspark-on-k8s

# Check Spark Operator logs
kubectl logs -n spark-operator deployment/my-spark-operator-controller

# View all events in the namespace
kubectl get events --sort-by='.lastTimestamp'

# Access Spark UI (if enabled)
kubectl port-forward pyspark-on-k8s-driver 4040:4040
# Then visit http://localhost:4040
```

## Cleanup

```bash
# Delete the SparkApplication
kubectl delete sparkapplication pyspark-on-k8s

# Verify cleanup
kubectl get pods -l spark-app-name=pyspark-on-k8s

# Remove the Docker image (optional)
docker rmi spark-k8s-app:2.0
```

## Next Steps

After successfully running this basic example:

1. **Explore Advanced Features**: Try examples with data sources (S3, HDFS, databases)
2. **Resource Optimization**: Experiment with different CPU/memory configurations
3. **Monitoring**: Set up Spark History Server and monitoring tools
4. **CI/CD Integration**: Automate image building and deployment
5. **Production Readiness**: Add proper logging, error handling, and configuration management

## Related Documentation

- [Spark Operator Installation](../../spark-operator/README.md)
- [Apache Spark on Kubernetes Guide](https://spark.apache.org/docs/latest/running-on-kubernetes.html)
- [Spark Operator Documentation](https://github.com/kubeflow/spark-operator)
- [Kubernetes Resource Management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
