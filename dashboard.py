import streamlit as st
import pandas as pd
from deltalake import DeltaTable
import plotly.express as px
import os

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Ventes Live",
    page_icon="📊",
    layout="wide"
)

# Titre
st.title("📊 Tableau de Bord des Ventes (Streaming -> Delta)")
st.markdown("Ce dashboard lit les données agrégées **Silver** générées par Spark.")

# Chemin vers vos données Silver (le même que dans streaming_silver.py)
SILVER_PATH = "delta_silver_aggreges"

def load_data():
    """Charge les données depuis la table Delta Lake locale."""
    if not os.path.exists(SILVER_PATH):
        return None
    
    try:
        # Lecture optimisée sans Spark
        dt = DeltaTable(SILVER_PATH)
        df = dt.to_pandas()
        return df
    except Exception as e:
        st.error(f"Erreur lors de la lecture Delta : {e}")
        return None

# Bouton pour rafraîchir
if st.button('🔄 Rafraîchir les données'):
    st.rerun()

# Chargement des données
df = load_data()

if df is None or df.empty:
    st.warning("⚠️ Aucune donnée trouvée ! Assurez-vous d'avoir lancé 'streaming_silver.py' au moins une fois.")
    st.info(f"Le dossier '{SILVER_PATH}' est introuvable ou vide.")
else:
    # --- KPIs (Indicateurs Clés) ---
    col1, col2, col3, col4 = st.columns(4)
    
    total_ca = df['total_depense'].sum()
    total_ventes = df['nb_achats'].sum()
    panier_moyen_global = total_ca / total_ventes if total_ventes > 0 else 0
    top_client = df.loc[df['total_depense'].idxmax()]['client_nom']

    col1.metric("💰 Chiffre d'Affaires", f"{total_ca:,.2f} €")
    col2.metric("📦 Volume Ventes", int(total_ventes))
    col3.metric("🛒 Panier Moyen", f"{panier_moyen_global:,.2f} €")
    col4.metric("🏆 Top Client", top_client)

    st.markdown("---")

    # --- Graphiques ---
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📊 Ventes par Client")
        fig_bar = px.bar(
            df, 
            x='client_nom', 
            y='total_depense', 
            color='segment',
            title="Qui dépense le plus ?",
            labels={'total_depense': "Dépenses (€)", 'client_nom': "Client"},
            text_auto='.2s'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("🌍 Répartition par Pays")
        # On groupe par pays pour le camembert
        df_pays = df.groupby('pays')['total_depense'].sum().reset_index()
        fig_pie = px.pie(
            df_pays, 
            values='total_depense', 
            names='pays', 
            title="Part de marché par pays",
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- Tableau de données ---
    st.subheader("📋 Détail des données Silver")
    st.dataframe(
        df.sort_values(by="total_depense", ascending=False),
        use_container_width=True,
        hide_index=True
    )