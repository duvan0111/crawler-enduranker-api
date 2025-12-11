"""
Utilitaires pour MongoDB et nettoyage de texte
Fonctions helper pour gérer les opérations courantes avec MongoDB
et le traitement de contenu HTML
"""

from bson import ObjectId
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
import re


def object_id_to_str(obj_id: ObjectId) -> str:
    """Convertir un ObjectId en string"""
    return str(obj_id)


def str_to_object_id(id_str: str) -> Optional[ObjectId]:
    """Convertir une string en ObjectId"""
    if not ObjectId.is_valid(id_str):
        return None
    return ObjectId(id_str)


def prepare_document_for_response(document: Dict[str, Any]) -> Dict[str, Any]:
    """
    Préparer un document MongoDB pour la réponse API
    Convertit les ObjectId en strings
    """
    if document and "_id" in document:
        document["_id"] = str(document["_id"])
    return document


def prepare_documents_for_response(documents: list) -> list:
    """
    Préparer une liste de documents MongoDB pour la réponse API
    """
    return [prepare_document_for_response(doc) for doc in documents]


def remove_none_values(data: dict) -> dict:
    """
    Supprimer les valeurs None d'un dictionnaire
    Utile pour les mises à jour partielles
    """
    return {k: v for k, v in data.items() if v is not None}


def nettoyer_html(html_content: str) -> str:
    """
    Nettoie le contenu HTML et extrait le texte propre
    
    Args:
        html_content: Contenu HTML brut
        
    Returns:
        Texte nettoyé et normalisé
    """
    if not html_content:
        return ""
    
    try:
        # Parser le HTML avec BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Supprimer les balises de script et de style
        for script in soup(['script', 'style', 'meta', 'noscript', 'header', 'footer', 'nav']):
            script.decompose()
        
        # Supprimer les commentaires HTML
        for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
            comment.extract()
        
        # Récupérer le texte
        texte = soup.get_text(separator=' ', strip=True)
        
        # Nettoyer le texte
        texte = normaliser_texte(texte)
        
        return texte
        
    except Exception as e:
        # En cas d'erreur, retourner le contenu brut
        return html_content


def normaliser_texte(texte: str) -> str:
    """
    Normalise le texte en supprimant les espaces multiples,
    les sauts de ligne excessifs, etc.
    
    Args:
        texte: Texte à normaliser
        
    Returns:
        Texte normalisé
    """
    if not texte:
        return ""
    
    # Supprimer les caractères de contrôle
    texte = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', texte)
    
    # Remplacer les multiples espaces par un seul
    texte = re.sub(r' +', ' ', texte)
    
    # Remplacer les multiples sauts de ligne par un double saut
    texte = re.sub(r'\n\s*\n+', '\n\n', texte)
    
    # Supprimer les espaces en début et fin de lignes
    lignes = [ligne.strip() for ligne in texte.split('\n')]
    texte = '\n'.join(lignes)
    
    # Supprimer les lignes vides multiples
    texte = re.sub(r'\n{3,}', '\n\n', texte)
    
    # Nettoyer les espaces avant/après
    texte = texte.strip()
    
    return texte


def nettoyer_texte_wikipedia(html_content: str) -> str:
    """
    Nettoie spécifiquement le contenu HTML de Wikipedia
    en supprimant les éléments non pertinents
    
    Args:
        html_content: Contenu HTML de Wikipedia
        
    Returns:
        Texte nettoyé
    """
    if not html_content:
        return ""
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Supprimer uniquement les éléments vraiment non pertinents
        elements_a_supprimer = [
            'script', 'style', 'meta', 'noscript',
            'header', 'footer', 'nav',
            # Éléments Wikipedia spécifiques à supprimer
            {'class': 'references'},  # Références
            {'class': 'reflist'},     # Liste de références
            {'class': 'navbox'},      # Boîtes de navigation
            {'class': 'mw-editsection'},  # Liens d'édition
            {'class': 'noprint'},     # Éléments non imprimables
            {'role': 'navigation'},   # Navigation
            {'id': 'siteSub'},        # Sous-titre du site
            {'id': 'jump-to-nav'},    # Liens de navigation
        ]
        
        for element in elements_a_supprimer:
            if isinstance(element, str):
                for tag in soup.find_all(element):
                    tag.decompose()
            elif isinstance(element, dict):
                for tag in soup.find_all(attrs=element):
                    tag.decompose()
        
        # Essayer plusieurs sélecteurs pour le contenu principal
        main_content = None
        
        # 1. Essayer mw-parser-output (nouveau format)
        main_content = soup.find('div', {'class': 'mw-parser-output'})
        
        # 2. Essayer mw-content-text (ancien format)
        if not main_content:
            main_content = soup.find('div', {'id': 'mw-content-text'})
        
        # 3. Essayer content (fallback)
        if not main_content:
            main_content = soup.find('div', {'id': 'content'})
        
        # 4. Dernier recours : bodyContent
        if not main_content:
            main_content = soup.find('div', {'id': 'bodyContent'})
        
        if main_content:
            texte = main_content.get_text(separator=' ', strip=True)
        else:
            # Fallback ultime sur le body
            body = soup.find('body')
            texte = body.get_text(separator=' ', strip=True) if body else soup.get_text(separator=' ', strip=True)
        
        # Normaliser le texte
        texte = normaliser_texte(texte)
        
        return texte
        
    except Exception as e:
        # En cas d'erreur, utiliser la fonction générique
        return nettoyer_html(html_content)


def tronquer_texte(texte: str, max_length: int = 5000) -> str:
    """
    Tronque un texte à une longueur maximale en préservant les mots
    
    Args:
        texte: Texte à tronquer
        max_length: Longueur maximale
        
    Returns:
        Texte tronqué
    """
    if not texte or len(texte) <= max_length:
        return texte
    
    # Tronquer au dernier espace avant max_length
    texte_tronque = texte[:max_length]
    dernier_espace = texte_tronque.rfind(' ')
    
    if dernier_espace > 0:
        texte_tronque = texte_tronque[:dernier_espace]
    
    return texte_tronque + "..."
