import time

from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("IcebergNessie").getOrCreate()

df = (
    spark.read.format("csv")
    .option("header", True)
    .option("inderSchema", True)
    .load("s3a://bronze/Churn_Modelling.csv")
)

spark.sql("CREATE NAMESPACE IF NOT EXISTS nessie.demo;")

spark.sql("DROP TABLE IF EXISTS nessie.demo.churn;")

spark.createDataFrame([], df.schema).writeTo("nessie.demo.churn").create()

df.write.format("iceberg").mode("overwrite").save("nessie.demo.churn")

df_from_iceberg = spark.table("nessie.demo.churn")
df_from_iceberg.show()

time.sleep(30)

spark.stop()
