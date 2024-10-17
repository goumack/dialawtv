import streamlit as st 
import pandas as pd
from datetime import datetime
import json
import os

# Chemin vers le fichier JSON
DATA_FILE = "livre_journal1.json"

# Vérifier si le fichier JSON existe, sinon créer un fichier vide avec les colonnes nécessaires
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

# Fonction pour charger les données à partir du fichier JSON
def load_data():
    with open(DATA_FILE, 'r') as f:
        data = pd.DataFrame(json.load(f))
        # Vérification des colonnes nécessaires
        if 'Débit' not in data.columns:
            data['Débit'] = 0.0
        if 'Crédit' not in data.columns:
            data['Crédit'] = 0.0
        if 'Date' not in data.columns:
            data['Date'] = pd.NaT  # Ajout d'une colonne Date vide si elle n'existe pas
        if 'Description' not in data.columns:  # Vérification de la colonne 'Description'
            data['Description'] = ""  # Ajout d'une colonne 'Description' vide
        return data

# Fonction pour sauvegarder les données dans le fichier JSON
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data.to_dict(orient='records'), f)

# Charger les données existantes
data = load_data()

# Initialiser des variables d'état pour les champs
if 'description' not in st.session_state:
    st.session_state.description = ""
if 'debit' not in st.session_state:
    st.session_state.debit = 0.0
if 'credit' not in st.session_state:
    st.session_state.credit = 0.0
if 'selected_entry' not in st.session_state:
    st.session_state.selected_entry = None

# Titre principal de l'application
st.markdown('<h1 class="title">Livre Journal de Dialaw TV</h1>', unsafe_allow_html=True)



# Section pour ajouter une nouvelle entrée dans le livre journal
st.markdown('<h2 class="section-title">Ajouter une nouvelle entrée</h2>', unsafe_allow_html=True)

# Formulaire pour ajouter une nouvelle entrée
st.session_state.description = st.text_input("Description de la transaction", value=st.session_state.description)
st.session_state.debit = st.number_input("Montant débit", min_value=0.0, value=st.session_state.debit, key="debit_input")
st.session_state.credit = st.number_input("Montant crédit", min_value=0.0, value=st.session_state.credit, key="credit_input")

if st.button("Ajouter l'entrée"):
    # Vérification des champs vides
    if not st.session_state.description or (st.session_state.debit <= 0 and st.session_state.credit <= 0):
        st.error("Veuillez remplir la description et au moins l'un des montants (débit ou crédit).")
    else:
        # Vérification des doublons
        is_duplicate = data[(data['Description'] == st.session_state.description) & 
                            (data['Débit'] == st.session_state.debit) & 
                            (data['Crédit'] == st.session_state.credit)]
        
        if not is_duplicate.empty:
            st.error("Cette entrée existe déjà dans le livre journal.")
        else:
            # Ajouter une nouvelle entrée dans le DataFrame
            new_entry = pd.DataFrame({
                'Date': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                'Description': [st.session_state.description],
                'Débit': [st.session_state.debit],
                'Crédit': [st.session_state.credit]
            })
            data = pd.concat([data, new_entry], ignore_index=True)
            
            # Sauvegarder les données mises à jour dans le fichier JSON
            save_data(data)
            
            st.success("Nouvelle entrée ajoutée avec succès !")
            
            # Réinitialiser les champs
            st.session_state.description = ""
            st.session_state.debit = 0.0
            st.session_state.credit = 0.0

# Section pour visualiser les données du journal
st.markdown('<h2 class="section-title">Journal des transactions</h2>', unsafe_allow_html=True)
st.dataframe(data)

# Calcul du solde total
if 'Débit' in data.columns and 'Crédit' in data.columns:
    solde = data['Débit'].sum() - data['Crédit'].sum()
    st.write(f"**Solde total** : {solde} CFA")

# Option pour exporter les données
st.download_button("Télécharger les données", data.to_csv().encode('utf-8'), "livre_journal.csv")

# ------------------ Statistiques en temps réel ------------------
st.markdown('<h2 class="section-title">Statistiques du mois en cours</h2>', unsafe_allow_html=True)

# Convertir la colonne 'Date' en format datetime
data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

# Filtrer les données pour le mois en cours
current_month = datetime.now().month
current_year = datetime.now().year
data_current_month = data[(data['Date'].dt.month == current_month) & (data['Date'].dt.year == current_year)]

# Calculer les totaux des débits et crédits pour le mois en cours
total_debit_month = data_current_month['Débit'].sum()
total_credit_month = data_current_month['Crédit'].sum()

# Afficher les statistiques
st.write(f"**Total des entrées (Débits) ce mois-ci :** {total_debit_month} CFA")
st.write(f"**Total des sorties (Crédits) ce mois-ci :** {total_credit_month} CFA")

# Calcul du solde pour le mois en cours
solde_month = total_debit_month - total_credit_month
st.write(f"**Solde du mois en cours :** {solde_month} CFA")

# Graphique des entrées et sorties du mois
st.markdown('<h3 class="section-title">Graphique des transactions du mois</h3>', unsafe_allow_html=True)
if not data_current_month.empty:
    st.bar_chart(data_current_month[['Débit', 'Crédit']])

