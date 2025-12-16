# producer_ventes.py
import json
import time
import random
from kafka import KafkaProducer
from datetime import datetime

# Configuration
KAFKA_TOPIC = "ventes_stream"
KAFKA_SERVER = "localhost:9092"

# Données de base
PRODUITS = [
    {"id": 101, "nom": "Ordinateur portable", "categorie": "Électronique", "prix": 899.99},
    {"id": 102, "nom": "Souris sans fil", "categorie": "Électronique", "prix": 25.50},
    {"id": 103, "nom": "Clavier mécanique", "categorie": "Électronique", "prix": 75.00},
    {"id": 104, "nom": "Casque audio", "categorie": "Électronique", "prix": 59.99},
    {"id": 105, "nom": "Livre 'Data Science'", "categorie": "Livre", "prix": 19.99},
]

CLIENTS = [
    {"id": 1, "nom": "Jean Dupont", "ville": "Paris", "pays": "France", "segment": "Particulier"},
    {"id": 2, "nom": "Maria Garcia", "ville": "Madrid", "pays": "Espagne", "segment": "Particulier"},
    {"id": 3, "nom": "John Smith", "ville": "Londres", "pays": "UK", "segment": "Entreprise"},
]

# Créer le producteur
producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

print("🚀 Démarrage du producteur Kafka...")

try:
    vente_id = 1
    while True:
        # Générer une vente aléatoire
        client = random.choice(CLIENTS)
        produit = random.choice(PRODUITS)
        quantite = random.randint(1, 3)
        montant = round(quantite * produit["prix"], 2)

        vente = {
            "vente_id": vente_id,
            "client_id": client["id"],
            "produit_id": produit["id"],
            "timestamp": datetime.now().isoformat(),
            "quantite": quantite,
            "montant": montant,
            "client_nom": client["nom"],
            "produit_nom": produit["nom"],
            "categorie": produit["categorie"],
            "pays": client["pays"],
            "segment": client["segment"]
        }

        # Envoyer au topic Kafka
        producer.send(KAFKA_TOPIC, value=vente)
        print(f"✅ Vente envoyée : {vente['vente_id']} - {vente['produit_nom']} - {vente['montant']}€")

        vente_id += 1
        time.sleep(2)  # 1 vente toutes les 2 secondes

except KeyboardInterrupt:
    print("🛑 Arrêt du producteur.")
    producer.close()