# streaming_silver.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# 1. Initialiser Spark
spark = SparkSession.builder \
    .appName("DeltaSilverLayer") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# 2. Lire la couche Bronze
# CORRECTION ICI : On lit le dossier créé par votre script streaming
# (Assurez-vous que ce dossier "delta_ventes_table" existe bien à côté de votre script)
print("Lecture des données depuis 'delta_ventes_table'...")
try:
    df_bronze = spark.read.format("delta").load("delta_ventes_table")
except Exception as e:
    print("ERREUR : Impossible de trouver le dossier 'delta_ventes_table'.")
    print("Vérifiez que le script spark_streaming_delta.py a bien tourné au moins une fois.")
    raise e

# 3. Transformations (Nettoyer + Agréger)
df_silver = df_bronze.groupBy("client_id", "client_nom", "pays", "segment", "jour").agg(
    sum("quantite").alias("total_quantite"),
    sum("montant").alias("total_depense"),
    count("*").alias("nb_achats"),
    avg("montant").alias("panier_moyen")
).withColumn("est_client_fidele", when(col("nb_achats") >= 2, True).otherwise(False))

# 4. Écrire en Silver
# On utilise aussi un chemin relatif pour éviter les bugs Windows
output_path = "delta_silver_aggreges"
df_silver.write.format("delta") \
    .mode("overwrite") \
    .option("mergeSchema", "true") \
    .save(output_path)

print(f" Données agrégées sauvegardées dans le dossier '{output_path}'")

# 5. Afficher un aperçu
print("--- Aperçu des Top Clients ---")
df_silver.orderBy(desc("total_depense")).show(10)