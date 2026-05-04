import requests
from typing import Optional, Tuple
import google.generativeai as genai
import os
import re

def get_lat_lng_from_address(address: str) -> Optional[Tuple[float, float]]:
    """
    Récupère les coordonnées géographiques (latitude, longitude) à partir d'une adresse
    en utilisant l'API Gemini (alternative gratuite sans CB à Google Maps Geocoding API).
    """
    if not address:
        return None
        
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("GOOGLE_API_KEY manquante pour le géocodage")
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = f"""Donne-moi uniquement les coordonnées GPS (latitude, longitude) de l'adresse suivante : "{address}, Algeria". 
        Format attendu : "XX.XXXXX, Y.YYYYY". Rien d'autre."""
        
        response = model.generate_content(prompt)
        text_response = response.text.strip()
        
        match = re.search(r"(-?\d+\.\d+),\s*(-?\d+\.\d+)", text_response)
        if match:
            lat = float(match.group(1))
            lng = float(match.group(2))
            return lat, lng
        else:
            print(f"Impossible d'extraire les coordonnées de la réponse Gemini : {text_response}")
            return None
            
    except Exception as e:
        print(f"Erreur lors du géocodage Gemini : {e}")
        return None
    return None