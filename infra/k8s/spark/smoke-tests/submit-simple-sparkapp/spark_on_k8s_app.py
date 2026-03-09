import time

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *

spark = SparkSession.builder.appName("Spark on K8s").getOrCreate()


df = (
    spark.range(1000000)
    .withColumn("plus_10", F.col("id") + 10)
    .withColumn("plus_20", F.col("id") + 20)
)

print("*******************************")

print(df.count())

df.printSchema()

df.show(100)

time.sleep(30)


print("Spark is shutting down....")

spark.stop()
