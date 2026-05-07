import requests
from typing import Optional, Tuple
import os

def get_lat_lng_from_address(address: str) -> Optional[Tuple[float, float]]:
    """
    Récupère les coordonnées géographiques (latitude, longitude) à partir d'une adresse
    en utilisant l'API Nominatim (OpenStreetMap).
    """
    if not address:
        return None
        
    try:
        # Nominatim nécessite un User-Agent clair
        headers = {
            'User-Agent': 'TutorlyApp/1.0'
        }
        clean_address = address
        if "Algeria" not in clean_address and "Algérie" not in clean_address:
            clean_address += ", Algeria"
            
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={requests.utils.quote(clean_address)}"
        
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if data and len(data) > 0:
            lat = float(data[0]['lat'])
            lng = float(data[0]['lon'])
            return lat, lng
        else:
            print(f"Aucun résultat trouvé pour l'adresse : {address}")
            return None
            
    except Exception as e:
        print(f"Erreur lors du géocodage Nominatim : {e}")
        return None