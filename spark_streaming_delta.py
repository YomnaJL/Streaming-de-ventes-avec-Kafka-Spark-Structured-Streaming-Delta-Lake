# spark_streaming_delta.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# 1. Initialiser Spark
spark = SparkSession.builder \
    .appName("KafkaToDeltaStreaming") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .config("spark.driver.memory", "2g") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# 2. Schéma des données
schema = StructType([
    StructField("vente_id", IntegerType(), True),
    StructField("client_id", IntegerType(), True),
    StructField("produit_id", IntegerType(), True),
    StructField("timestamp", StringType(), True),
    StructField("quantite", IntegerType(), True),
    StructField("montant", DoubleType(), True),
    StructField("client_nom", StringType(), True),
    StructField("produit_nom", StringType(), True),
    StructField("categorie", StringType(), True),
    StructField("pays", StringType(), True),
    StructField("segment", StringType(), True)
])

# 3. Lire depuis Kafka
df_kafka = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "ventes_stream") \
    .option("startingOffsets", "earliest") \
    .load()

# 4. Parser les données JSON
df_parsed = df_kafka.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

# 5. Enrichissement (Ajout date pour partitionnement)
df_enriched = df_parsed \
    .withColumn("date_ingestion", current_timestamp()) \
    .withColumn("jour", substring(col("timestamp"), 1, 10))

# 6. Écrire en Delta Lake
# Note : Sur Windows, il est préférable d'utiliser des chemins relatifs ou C:/tmp
query = df_enriched.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "checkpoint_ventes") \
    .partitionBy("jour") \
    .start("delta_ventes_table")

# Correction de la ligne qui posait problème (on enlève l'émoji et les accents complexes)
print("--- Streaming demarre. Ecriture en Delta Lake en cours ---")

query.awaitTermination()