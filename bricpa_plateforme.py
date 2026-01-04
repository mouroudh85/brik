"""
🏗️ BricPa - Plateforme de Mise en Relation
Clients ↔️ Artisans pour devis de travaux
"""

import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import os
from datetime import datetime
import pandas as pd

# Configuration API
API_KEY = "AIzaSyCQjaXwgbzL6tL7DnrcbdTqI9qXt1_rQIo"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-exp")

# Configuration page
st.set_page_config(
    page_title="BricPa - Plateforme Travaux",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .urgent-badge {
        background: #ef4444;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
    }
    .normal-badge {
        background: #10b981;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    .devis-card {
        border-left: 4px solid #667eea;
        padding-left: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Fichiers de données
DATA_DIR = "data_plateforme"
DEMANDES_FILE = os.path.join(DATA_DIR, "demandes.json")
DEVIS_FILE = os.path.join(DATA_DIR, "devis.json")
ARTISANS_FILE = os.path.join(DATA_DIR, "artisans.json")
PHOTOS_DIR = os.path.join(DATA_DIR, "photos")

# Créer les dossiers si nécessaire
for folder in [DATA_DIR, PHOTOS_DIR]:
    os.makedirs(folder, exist_ok=True)

# Fonctions de gestion des données
def load_json(filepath, default=None):
    """Charger un fichier JSON"""
    if default is None:
        default = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default

def save_json(filepath, data):
    """Sauvegarder un fichier JSON"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_next_id(items):
    """Obtenir le prochain ID"""
    if not items:
        return 1
    return max(item['id'] for item in items) + 1

# Initialisation session state
if 'role' not in st.session_state:
    st.session_state.role = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'artisan_profile' not in st.session_state:
    st.session_state.artisan_profile = None

# ==================== SÉLECTION DU RÔLE ====================
def show_role_selection():
    st.markdown("""
    <div class="main-header">
        <h1>🏗️ BricPa</h1>
        <p style='font-size: 1.2rem; margin-top: 1rem;'>
            Plateforme de mise en relation pour vos travaux
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card">
            <h2>👤 Je suis un Client</h2>
            <p>Je cherche un artisan pour mes travaux</p>
            <ul>
                <li>Publier une demande de travaux</li>
                <li>Recevoir des devis</li>
                <li>Comparer et choisir</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Continuer en tant que Client", use_container_width=True, type="primary"):
            st.session_state.role = "client"
            st.session_state.user_id = f"client_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="card">
            <h2>👷 Je suis un Artisan</h2>
            <p>Je propose mes services</p>
            <ul>
                <li>Consulter les demandes de travaux</li>
                <li>Envoyer des devis</li>
                <li>Développer mon activité</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔧 Continuer en tant qu'Artisan", use_container_width=True, type="primary"):
            st.session_state.role = "artisan"
            st.rerun()

# ==================== INTERFACE CLIENT ====================
def show_client_interface():
    st.sidebar.success(f"✅ Connecté en tant que **Client**")
    st.sidebar.button("🔄 Changer de rôle", on_click=lambda: st.session_state.clear())
    
    st.markdown("""
    <div class="main-header">
        <h1>👤 Espace Client</h1>
        <p>Publiez votre demande et recevez des devis</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📝 Nouvelle demande", "📊 Mes demandes", "💬 Assistant IA"])
    
    with tab1:
        show_new_demande_form()
    
    with tab2:
        show_client_demandes()
    
    with tab3:
        show_chat_assistant()

def show_new_demande_form():
    st.subheader("📝 Publier une demande de travaux")
    
    with st.form("nouvelle_demande"):
        col1, col2 = st.columns(2)
        
        with col1:
            type_travaux = st.selectbox(
                "Type de travaux *",
                ["Peinture", "Plomberie", "Électricité", "Rénovation complète", 
                 "Fenêtres/Portes", "Sol/Carrelage", "Maçonnerie", "Menuiserie", "Autre"]
            )
            
            ville = st.text_input("Ville / Code postal *", placeholder="Ex: Marseille 13001")
            
            urgence = st.radio("Urgence", ["Normal", "Urgent"], horizontal=True)
        
        with col2:
            budget = st.text_input("Budget estimatif (optionnel)", placeholder="Ex: 2000-3000€")
            
            st.write("**Photos du chantier**")
            photos = st.file_uploader(
                "Ajoutez 1 à 5 photos",
                type=['jpg', 'jpeg', 'png'],
                accept_multiple_files=True,
                key="photos_demande"
            )
        
        description = st.text_area(
            "Description détaillée de vos besoins *",
            placeholder="Décrivez précisément les travaux à réaliser...",
            height=150
        )
        
        submitted = st.form_submit_button("🚀 Publier ma demande", use_container_width=True, type="primary")
        
        if submitted:
            if not description or not ville:
                st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
            elif photos and len(photos) > 5:
                st.error("❌ Maximum 5 photos")
            else:
                # Sauvegarder les photos
                photo_paths = []
                if photos:
                    for i, photo in enumerate(photos):
                        photo_filename = f"demande_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}.jpg"
                        photo_path = os.path.join(PHOTOS_DIR, photo_filename)
                        img = Image.open(photo)
                        img.save(photo_path)
                        photo_paths.append(photo_filename)
                
                # Analyser avec Gemini si photos disponibles
                analyse_ia = ""
                if photos:
                    with st.spinner("🤖 Analyse IA de vos photos..."):
                        try:
                            img = Image.open(photos[0])
                            prompt = f"""Analyse cette photo de chantier pour des travaux de {type_travaux}.
                            
Donne une estimation rapide:
1. Surface approximative en m²
2. État actuel
3. Principaux travaux nécessaires
4. Estimation de prix (fourchette basse-haute)

Sois concis (max 150 mots)."""
                            response = model.generate_content([prompt, img])
                            analyse_ia = response.text
                        except:
                            analyse_ia = "Analyse non disponible"
                
                # Créer la demande
                demandes = load_json(DEMANDES_FILE)
                nouvelle_demande = {
                    'id': get_next_id(demandes),
                    'client_id': st.session_state.user_id,
                    'type_travaux': type_travaux,
                    'description': description,
                    'ville': ville,
                    'urgence': urgence,
                    'budget': budget,
                    'photos': photo_paths,
                    'analyse_ia': analyse_ia,
                    'date_creation': datetime.now().isoformat(),
                    'statut': 'active',
                    'nb_devis': 0
                }
                demandes.append(nouvelle_demande)
                save_json(DEMANDES_FILE, demandes)
                
                st.success("✅ Votre demande a été publiée avec succès!")
                st.balloons()
                
                if analyse_ia:
                    st.info(f"**🤖 Analyse IA:**\n\n{analyse_ia}")
                
                st.rerun()

def show_client_demandes():
    st.subheader("📊 Mes demandes de travaux")
    
    demandes = load_json(DEMANDES_FILE)
    mes_demandes = [d for d in demandes if d['client_id'] == st.session_state.user_id]
    
    if not mes_demandes:
        st.info("📭 Vous n'avez pas encore publié de demande")
        return
    
    for demande in reversed(mes_demandes):
        with st.expander(f"🏗️ {demande['type_travaux']} - {demande['ville']} ({demande['nb_devis']} devis reçus)"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Description:** {demande['description']}")
                st.write(f"**Date:** {demande['date_creation'][:10]}")
                if demande['budget']:
                    st.write(f"**Budget:** {demande['budget']}")
                
                # Photos
                if demande['photos']:
                    st.write("**Photos:**")
                    cols = st.columns(min(len(demande['photos']), 3))
                    for i, photo in enumerate(demande['photos']):
                        with cols[i % 3]:
                            img_path = os.path.join(PHOTOS_DIR, photo)
                            if os.path.exists(img_path):
                                st.image(img_path, use_container_width=True)
            
            with col2:
                if demande['urgence'] == 'Urgent':
                    st.markdown('<span class="urgent-badge">🔥 URGENT</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="normal-badge">✅ Normal</span>', unsafe_allow_html=True)
            
            # Afficher les devis reçus
            show_devis_for_demande(demande['id'])

def show_devis_for_demande(demande_id):
    st.markdown("---")
    st.write("### 📨 Devis reçus")
    
    devis_list = load_json(DEVIS_FILE)
    devis_demande = [d for d in devis_list if d['demande_id'] == demande_id]
    
    if not devis_demande:
        st.info("Aucun devis reçu pour le moment")
        return
    
    for devis in devis_demande:
        artisan = get_artisan_by_id(devis['artisan_id'])
        artisan_name = artisan['nom'] if artisan else "Artisan"
        
        st.markdown(f"""
        <div class="card devis-card">
            <h4>👷 {artisan_name}</h4>
            <p><strong>Prix:</strong> {devis['prix']}€</p>
            <p><strong>Délai:</strong> {devis['delai']}</p>
            <p><strong>Message:</strong> {devis['message']}</p>
            <p style='font-size: 0.85rem; color: #666;'>Envoyé le {devis['date_envoi'][:10]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"✅ Accepter ce devis", key=f"accept_{devis['id']}"):
            st.success("🎉 Devis accepté! L'artisan sera notifié.")
            # TODO: Implémenter notification

# ==================== INTERFACE ARTISAN ====================
def show_artisan_interface():
    # Vérifier si profil existe
    artisans = load_json(ARTISANS_FILE, default=[])
    artisan_profile = next((a for a in artisans if a.get('session_id') == st.session_state.get('artisan_session_id')), None)
    
    if not artisan_profile:
        show_artisan_registration()
    else:
        st.session_state.artisan_profile = artisan_profile
        show_artisan_dashboard()

def show_artisan_registration():
    st.markdown("""
    <div class="main-header">
        <h1>👷 Inscription Artisan</h1>
        <p>Créez votre profil pour commencer</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("inscription_artisan"):
        nom = st.text_input("Nom / Entreprise *", placeholder="Ex: Dupont Rénovation")
        
        col1, col2 = st.columns(2)
        with col1:
            metier = st.selectbox(
                "Métier *",
                ["Peinture", "Plomberie", "Électricité", "Rénovation générale",
                 "Maçonnerie", "Menuiserie", "Sol/Carrelage", "Multi-services"]
            )
        
        with col2:
            zone = st.text_input("Zone d'intervention *", placeholder="Ex: Marseille et alentours")
        
        description = st.text_area(
            "Présentation *",
            placeholder="Décrivez votre entreprise, votre expérience...",
            height=120
        )
        
        telephone = st.text_input("Téléphone", placeholder="06 12 34 56 78")
        
        submitted = st.form_submit_button("✅ Créer mon profil", type="primary", use_container_width=True)
        
        if submitted:
            if not nom or not metier or not zone or not description:
                st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
            else:
                artisans = load_json(ARTISANS_FILE, default=[])
                session_id = f"artisan_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                nouveau_artisan = {
                    'id': get_next_id(artisans) if artisans else 1,
                    'session_id': session_id,
                    'nom': nom,
                    'metier': metier,
                    'zone': zone,
                    'description': description,
                    'telephone': telephone,
                    'date_inscription': datetime.now().isoformat(),
                    'nb_devis_envoyes': 0
                }
                
                artisans.append(nouveau_artisan)
                save_json(ARTISANS_FILE, artisans)
                
                st.session_state.artisan_session_id = session_id
                st.session_state.artisan_profile = nouveau_artisan
                
                st.success("✅ Profil créé avec succès!")
                st.balloons()
                st.rerun()

def show_artisan_dashboard():
    profile = st.session_state.artisan_profile
    
    st.sidebar.success(f"✅ Connecté: **{profile['nom']}**")
    st.sidebar.write(f"**Métier:** {profile['metier']}")
    st.sidebar.write(f"**Zone:** {profile['zone']}")
    
    if st.sidebar.button("🔄 Changer de rôle"):
        st.session_state.clear()
        st.rerun()
    
    st.markdown(f"""
    <div class="main-header">
        <h1>👷 Tableau de bord - {profile['nom']}</h1>
        <p>Consultez les demandes et envoyez vos devis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Statistiques rapides
    col1, col2, col3 = st.columns(3)
    demandes = load_json(DEMANDES_FILE)
    demandes_pertinentes = [d for d in demandes if d['type_travaux'] == profile['metier'] and d['statut'] == 'active']
    
    with col1:
        st.metric("📋 Demandes disponibles", len(demandes_pertinentes))
    with col2:
        st.metric("📨 Devis envoyés", profile['nb_devis_envoyes'])
    with col3:
        st.metric("⭐ Taux de réponse", f"{min(100, profile['nb_devis_envoyes'] * 10)}%")
    
    st.markdown("---")
    
    # Liste des demandes
    st.subheader("📋 Demandes de travaux correspondantes")
    
    if not demandes_pertinentes:
        st.info(f"📭 Aucune demande pour '{profile['metier']}' pour le moment")
        return
    
    for demande in reversed(demandes_pertinentes):
        with st.expander(f"🏗️ {demande['type_travaux']} à {demande['ville']} - {demande['urgence']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Description:** {demande['description']}")
                if demande['budget']:
                    st.write(f"**Budget client:** {demande['budget']}")
                st.write(f"**Date:** {demande['date_creation'][:10]}")
                
                # Photos
                if demande['photos']:
                    st.write("**Photos du chantier:**")
                    cols = st.columns(min(len(demande['photos']), 3))
                    for i, photo in enumerate(demande['photos']):
                        with cols[i % 3]:
                            img_path = os.path.join(PHOTOS_DIR, photo)
                            if os.path.exists(img_path):
                                st.image(img_path, use_container_width=True)
                
                # Analyse IA
                if demande.get('analyse_ia'):
                    with st.expander("🤖 Voir l'analyse IA"):
                        st.info(demande['analyse_ia'])
            
            with col2:
                if demande['urgence'] == 'Urgent':
                    st.markdown('<span class="urgent-badge">🔥 URGENT</span>', unsafe_allow_html=True)
                
                # Vérifier si devis déjà envoyé
                devis_list = load_json(DEVIS_FILE)
                already_sent = any(d['demande_id'] == demande['id'] and d['artisan_id'] == profile['id'] for d in devis_list)
                
                if already_sent:
                    st.success("✅ Devis déjà envoyé")
                else:
                    if st.button("📤 Envoyer un devis", key=f"devis_{demande['id']}"):
                        show_devis_form(demande)

def show_devis_form(demande):
    st.markdown("### 📤 Envoyer votre devis")
    
    with st.form(f"form_devis_{demande['id']}"):
        prix = st.number_input("Prix (€) *", min_value=0, step=100, value=1000)
        delai = st.text_input("Délai de réalisation *", placeholder="Ex: 2 semaines")
        message = st.text_area(
            "Message au client *",
            placeholder="Présentez votre offre, votre expérience...",
            height=120
        )
        
        submitted = st.form_submit_button("✅ Envoyer le devis", type="primary")
        
        if submitted:
            if not delai or not message:
                st.error("❌ Veuillez remplir tous les champs")
            else:
                devis_list = load_json(DEVIS_FILE)
                
                nouveau_devis = {
                    'id': get_next_id(devis_list) if devis_list else 1,
                    'demande_id': demande['id'],
                    'artisan_id': st.session_state.artisan_profile['id'],
                    'prix': prix,
                    'delai': delai,
                    'message': message,
                    'date_envoi': datetime.now().isoformat(),
                    'statut': 'envoye'
                }
                
                devis_list.append(nouveau_devis)
                save_json(DEVIS_FILE, devis_list)
                
                # Mettre à jour le compteur de devis
                demandes = load_json(DEMANDES_FILE)
                for d in demandes:
                    if d['id'] == demande['id']:
                        d['nb_devis'] = d.get('nb_devis', 0) + 1
                save_json(DEMANDES_FILE, demandes)
                
                # Mettre à jour profil artisan
                artisans = load_json(ARTISANS_FILE)
                for a in artisans:
                    if a['id'] == st.session_state.artisan_profile['id']:
                        a['nb_devis_envoyes'] = a.get('nb_devis_envoyes', 0) + 1
                        st.session_state.artisan_profile = a
                save_json(ARTISANS_FILE, artisans)
                
                st.success("✅ Votre devis a été envoyé avec succès!")
                st.balloons()
                st.rerun()

def get_artisan_by_id(artisan_id):
    artisans = load_json(ARTISANS_FILE, default=[])
    return next((a for a in artisans if a['id'] == artisan_id), None)

# ==================== CHAT ASSISTANT IA ====================
def show_chat_assistant():
    st.subheader("💬 Assistant IA - Posez vos questions sur vos travaux")
    st.info("🤖 Je peux vous conseiller sur les types de travaux, les prix moyens, les matériaux, etc.")
    
    # Initialiser l'historique du chat
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    # Afficher l'historique
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Zone de saisie
    if prompt := st.chat_input("Posez votre question (ex: Quel est le prix moyen pour repeindre une pièce ?)"):
        # Ajouter le message utilisateur
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Générer la réponse
        with st.chat_message("assistant"):
            with st.spinner("Réflexion en cours..."):
                try:
                    # Contexte pour l'assistant
                    context = """Tu es un assistant expert en travaux et rénovation.
Tu aides les clients à comprendre leurs besoins, estimer les coûts, choisir les matériaux.
Donne des réponses claires, précises et avec des fourchettes de prix réalistes.
Sois concis (max 200 mots) et pratique."""
                    
                    full_prompt = f"{context}\n\nQuestion: {prompt}"
                    response = model.generate_content(full_prompt)
                    answer = response.text
                    
                    st.markdown(answer)
                    st.session_state.chat_messages.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    error_msg = f"Erreur: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
    
    # Bouton pour réinitialiser
    if st.button("🔄 Nouvelle conversation"):
        st.session_state.chat_messages = []
        st.rerun()

# ==================== MAIN ====================
def main():
    if not st.session_state.role:
        show_role_selection()
    elif st.session_state.role == "client":
        show_client_interface()
    elif st.session_state.role == "artisan":
        show_artisan_interface()

if __name__ == "__main__":
    main()
