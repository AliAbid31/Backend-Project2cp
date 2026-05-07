import os
import json
import requests  
import re
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = "google/gemini-2.5-pro"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

ES_LEVELS = ["1CP Esi", "2CP Esi", "1CS Esi", "2CS Esi", "3CS Esi", "1CP", "2CP"
             , "1CS", "2CS", "3CS", "esi 1cp", "esi 2cp", "esi 1cs", "esi 2cs", "esi 3cs", 
             "university 1cp", "university 2cp", "university 1cs", 
             "university 2cs", "university 3cs","pfe"]
CEM_LEVELS = ["1AM", "2AM", "3AM", "4AM","bem"]
LYCEE_LEVELS = ["1AS", "2AS", "3AS","bac"]
PRIMAIRE_LEVELS = ["1AP", "2AP", "3AP", "4AP", "5AP", "primary1", "primary2", "primary3", "primary4", "primary5"]

# Dictionnaire etendu pour les matieres (francais et arabe supportes)

SUBJECT_MAP = {
    # --- TRONC COMMUN (Primaire, Moyen, Lycée) ---
    "maths": "Mathematics", "math": "Mathematics", "رياضيات": "Mathematics", "mathematiques": "Mathematics",
    "arabe": "Arabic", "لغة عربية": "Arabic", "عربية": "Arabic",
    "islamia": "Islamic ", "تربية إسلامية": "Islamic education", "اسلامية": "Islamic education",
    "français": "French", "francais": "French", "فرنسية": "French", "fr": "French",
    "anglais": "English", "english": "English", "انجليزية": "English", "eng": "English",
    "physique": "Physics", "فيزياء": "Physics", "phys": "Physics", "physics": "Physics",
    "science": "Natural and life Science", "علوم": "Natural and life Science", "snv": "Natural and life Science",
    "histoire": "History", "géographie": "Geography", "تاريخ": "History", "جغرافيا": "Geography", "hg": "History & Geography",
    "civique": "Civil education", "تربية مدنية": "Civil education",
    
    # --- LYCÉE : FILIÈRES TECHNIQUES & SPÉCIALISÉES ---
    "philo": "Philosophy", "philosophie": "Philosophy", "فلسفة": "Philosophy",
    "mecanique": "Mechanical engineering", "mécanique": "Mechanical engineering", "هندسة ميكانيكية": "Mechanical engineering",
    "genie civil": "Civil engineering", "civil": "Civil engineering", "هندسة مدنية": "Civil engineering",
    "electrique": "Electrical engineering", "هندسة كهربائية": "Electrical engineering",
    "economie": "Economics", "إقتصاد": "Economics", "management": "Management", "تسيير": "Management",
    
    # --- UNIVERSITY : ESI 1CP (Semestre 1 & 2) ---
    "ana1": "ANA1", "analyse 1": "ANA1", "alg1": "ALG1", "algebre 1": "ALG1",
    "alsds": "ALSDS", "algo": "ALSDS", "archi1": "ARCHI1", "architecture 1": "ARCHI1",
    "sys1": "SYS1", "système 1": "SYS1", "elect": "ELECT", "electricite": "ELECT",
    "bweb": "BWEB", "web": "BWEB", "tee": "TEE",
    "ana2": "ANA2", "alg2": "ALG2", "sys2": "SYS2", "alsdd": "ALSDD",
    "elecf1": "ELECF1", "meca": "MECA", "mecanique": "MECA", "teo": "TEO",
    
    # --- UNIVERSITY : ESI 2CP (Semestre 1 & 2) ---
    "ana3": "ANA3", "alg3": "ALG3", "sfsd": "SFSD", "fichiers": "SFSD",
    "archi2": "ARCHI2", "prst1": "PRST1", "proba1": "PRST1", "elecf2": "ELECF2",
    "econ": "ECON", "economie_esi": "ECON", "ana4": "ANA4", "prst2": "PRST2",
    "poo": "POO", "java": "POO", "ooe": "OOE", "sinf": "SINF", "logm": "LOGM",
    "university": "University",
    
    # --- UNIVERSITY : ESI 1CS (Semestre 1 & 2) ---
    "anum": "ANUM", "igl": "IGL", "genie logiciel": "IGL", "orga": "ORGA",
    "res1": "RES1", "reseau 1": "RES1", "ro": "RO", "recherche op": "RO",
    "syc": "SYC", "bdd": "BDD", "base de données": "BDD", "sql": "BDD",
    "sec": "SEC", "securité": "SEC", "cyber": "SEC",
    
    # --- UNIVERSITY : ESI 2CS (Spécialités SID, SIQ, SIL, SIT) ---
    "ml": "ML", "machine learning": "ML", "ai": "ML", "nlp": "NLP",
    "bi": "BI", "business intelligence": "BI", "data": "BI",
    "compil": "COMPIL", "compilation": "COMPIL", "optm": "OPTM",
    "ihm": "IHM", "ux": "IHM", "web_adv": "WEB", "erp": "ERP",
    "audit": "AUDIT", "crm": "CRM"
}

NAME_STOPWORDS = {
    "teacher", "prof", "professeur", "tutor", "cours", "course", "lesson",
    "cherche", "recherche", "search", "find", "looking", "for", "avec",
    "de", "du", "des", "le", "la", "les", "un", "une", "et", "and",
    "in", "at", "a", "avec", "fi", "min", "مع", "من", "في", "استاذ",
    "أستاذ", "استاذة", "أستاذة"
}

MODE_KEYWORDS = {
    "enligne", "online", "distance", "عن", "بعد", "أونلاين", "chez", "moi",
    "domicile", "المنزل", "في", "حضوريا", "onsite"
}


def _format_name_token(token: str) -> str:
    if re.fullmatch(r"[a-z]+", token):
        return token.capitalize()
    return token


def infer_full_name_by_elimination(cleaned_query: str, known_terms: set):
    """Infer person name by removing known city/subject/level/mode tokens."""
    tokens = re.findall(r"[a-zA-Z0-9\u0600-\u06FF]+", cleaned_query)
    remaining = [
        t for t in tokens
        if t not in known_terms
        and t not in NAME_STOPWORDS
        and len(t) > 1
        and not any(ch.isdigit() for ch in t)
    ]

    if not remaining or len(remaining) > 4:
        return None

    return " ".join(_format_name_token(token) for token in remaining)


def normalize_extracted_criteria(criteria: dict, original_query: str):
    """Normalize model output keys to backend search keys."""
    normalized = {
        "role": criteria.get("role") or criteria.get("type") or "teacher",
        "full_name": criteria.get("full_name"),
        "postal_address": criteria.get("postal_address"),
        "subject": criteria.get("subject"),
        "level": criteria.get("level") or criteria.get("teaching_level"),
        "availability": criteria.get("availability") or criteria.get("education_mode"),
        "deplacement": criteria.get("deplacement"),
        "domain": criteria.get("domain"),
        "price_operator": criteria.get("price_operator"),
        "price_value": criteria.get("price_value")
    }

    for key, value in normalized.items():
        if isinstance(value, str):
            trimmed = value.strip()
            if trimmed.lower() in {"none", "null", ""}:
                normalized[key] = None
            else:
                normalized[key] = trimmed

    if normalized.get("role"):
        normalized["role"] = str(normalized["role"]).lower()

    if not normalized.get("full_name"):
        fallback_name = local_keyword_extraction(original_query).get("full_name")
        if fallback_name:
            normalized["full_name"] = fallback_name

    return normalized

def clean_query(q: str):
    # Support des caracteres arabes et latins
    return re.sub(r"[^\w\s\u0600-\u06FF]", "", q.lower())

def local_keyword_extraction(query: str):
    q = clean_query(query)
    results = {
        "role": "teacher",
        "full_name": None,
        "postal_address": None,
        "subject": None,
        "level": None,
        "availability": None,
        "deplacement": None,
        "domain": None
    }

    # Recherche de niveau
    for lvl in (ES_LEVELS + CEM_LEVELS + LYCEE_LEVELS + PRIMAIRE_LEVELS):
        if re.search(rf'\b{re.escape(lvl.lower())}\b', q):
            results["level"] = lvl
            break
    
    # Check for "university" explicitly if no specific code found
    if not results["level"] and "university" in q:
        results["level"] = "University"

    # Recherche de matiere (match partiel ou complet)
    for key, val in SUBJECT_MAP.items():
        if re.search(rf'\b{re.escape(key)}\b', q):
            results["subject"] = val
            break

    # Villes algeriennes courantes (Francais/Arabe)
    cities =  {
       "adrar": "Adrar", "أدرار": "Adrar",
    "chlef": "Chlef", "الشلف": "Chlef",
    "laghouat": "Laghouat", "الأغواط": "Laghouat",
    "oum el bouaghi": "Oum El Bouaghi", "أم البواقي": "Oum El Bouaghi",
    "batna": "Batna", "باتنة": "Batna",
    "bejaia": "Bejaia", "بجاية": "Bejaia",
    "biskra": "Biskra", "بسكرة": "Biskra",
    "bechar": "Bechar", "بشار": "Bechar",
    "blida": "Blida", "البليدة": "Blida",
    "bouira": "Bouira", "البويرة": "Bouira",

    # 11-20
    "tamanrasset": "Tamanrasset", "تمنراست": "Tamanrasset",
    "tebessa": "Tebessa", "تبسة": "Tebessa",
    "tlemcen": "Tlemcen", "تلمسان": "Tlemcen",
    "tiaret": "Tiaret", "تيارت": "Tiaret",
    "tizi ouzou": "Tizi Ouzou", "تيزي وزو": "Tizi Ouzou",
    "algiers": "Alger", "alger": "Alger", "الجزائر": "Alger",
    "djelfa": "Djelfa", "الجلفة": "Djelfa",
    "jijel": "Jijel", "جيجل": "Jijel",
    "setif": "Setif", "سطيف": "Setif",
    "saida": "Saida", "سعيدة": "Saida",

    # 21-30
    "skikda": "Skikda", "سكيكدة": "Skikda",
    "sidi bel abbes": "Sidi Bel Abbes", "سيدي بلعباس": "Sidi Bel Abbes",
    "annaba": "Annaba", "عنابة": "Annaba",
    "guelma": "Guelma", "قالمة": "Guelma",
    "constantine": "Constantine", "قسنطينة": "Constantine",
    "medea": "Medea", "المدية": "Medea",
    "mostaganem": "Mostaganem", "مستغانم": "Mostaganem",
    "msila": "M'Sila", "المسيلة": "M'Sila",
    "mascara": "Mascara", "معسكر": "Mascara",
    "ouargla": "Ouargla", "ورقلة": "Ouargla",

    # 31-40
    "oran": "Oran", "وهران": "Oran",
    "el bayadh": "El Bayadh", "البيض": "El Bayadh",
    "illizi": "Illizi", "إليزي": "Illizi",
    "bordj bou arreridj": "Bordj Bou Arreridj", "bba": "Bordj Bou Arreridj", "برج بوعريريج": "Bordj Bou Arreridj",
    "boumerdes": "Boumerdes", "بومرداس": "Boumerdes",
    "el tarf": "El Tarf", "الطارف": "El Tarf",
    "tindouf": "Tindouf", "تندوف": "Tindouf",
    "tissemsilt": "Tissemsilt", "تيسمسيلت": "Tissemsilt",
    "el oued": "El Oued", "الوادي": "El Oued",
    "khenchela": "Khenchela", "خنشلة": "Khenchela",

    # 41-48
    "souk ahras": "Souk Ahras", "سوق أهراس": "Souk Ahras",
    "tipaza": "Tipaza", "تيبازة": "Tipaza",
    "mila": "Mila", "ميلة": "Mila",
    "ain defla": "Ain Defla", "عين الدفلى": "Ain Defla",
    "naama": "Naama", "النعامة": "Naama",
    "ain temouchent": "Ain Temouchent", "عين تموشنت": "Ain Temouchent",
    "ghardaia": "Ghardaia", "غرداية": "Ghardaia",
    "relizane": "Relizane", "غليزان": "Relizane",

    # 49-58 (New Wilayas)
    "timimoun": "Timimoun", "تيميمون": "Timimoun",
    "bordj badji mokhtar": "Bordj Badji Mokhtar", "برج باجي مختار": "Bordj Badji Mokhtar",
    "ouled djellal": "Ouled Djellal", "أولاد جلال": "Ouled Djellal",
    "beni abbes": "Beni Abbes", "بني عباس": "Beni Abbes",
    "in salah": "In Salah", "عين صالح": "In Salah",
    "in guezzam": "In Guezzam", "عين قزام": "In Guezzam",
    "touggourt": "Touggourt", "تقرت": "Touggourt",
    "djanet": "Djanet", "جانت": "Djanet",
    "el m'ghair": "El M'Ghair", "المغير": "El M'Ghair",
    "el meniaa": "El Meniaa", "المنيعة": "El Meniaa"
    }
    for city_key, city_val in cities.items():
        if re.search(rf'\b{re.escape(city_key)}\b', q):
            results["postal_address"] = city_val
            break

    # Modalites
    if any(k in q for k in ["enligne", "online", "distance", "عن بعد", "أونلاين"]):
        results["availability"] = "online"
    elif any(k in q for k in ["chez moi", "domicile", "في المنزل", "حضوريا", "onsite"]):
        results["availability"] = "onsite"
        results["deplacement"] = "yes"

    known_terms = set(MODE_KEYWORDS)
    for lvl in (ES_LEVELS + CEM_LEVELS + LYCEE_LEVELS + PRIMAIRE_LEVELS):
        known_terms.update(clean_query(lvl).split())
    for subject_key in SUBJECT_MAP.keys():
        known_terms.update(clean_query(subject_key).split())
    for city_key in cities.keys():
        known_terms.update(clean_query(city_key).split())

    if not results["full_name"]:
        results["full_name"] = infer_full_name_by_elimination(q, known_terms)

    return results

def extract_search_criteria(query: str):
    """
    Extract search criteria from user query using OpenRouter's Gemini Flash.
    Falls back to local pattern matching if API fails.
    Uses a single API key.
    """
    if not query or len(query.strip()) < 3:
        return local_keyword_extraction("")

    if not OPENROUTER_API_KEY:
        print("INFO: OPENROUTER_API_KEY not configured. Using local pattern matching.")
        return local_keyword_extraction(query)

    prompt = f"""You are an expert intelligent query parser for a mobile education tutoring platform. Your task is to convert a user's natural language search input into a precise JSON object for database querying.

Contextual Knowledge (Levels & Subjects): You must use the following hierarchy and mappings to identify the level and subject fields. Be very precise.

**Subject Mapping Rules (High Priority):**
- "maths", "mathematiques", "math", "رياضيات" -> "Mathematics"
- "algebra", "algebre", "alg" -> If context is "1CP", map to "ALG1". If "2CP", map to "ALG3".
- "analyse", "analysis" -> If context is "1CP", map to "ANA1". If "2CP", map to "ANA3".
- "physique", "physics", "فيزياء" -> "Physics"
- "science", "علوم" -> "Natural and life Science"
- "poo", "java" -> "POO"
- "bdd", "sql", "base de données" -> "BDD"
- "réseau", "res" -> "RES1"
- "igl", "genie logiciel" -> "IGL"
- "français", "francais", "فرنسية" -> "French"
- "anglais", "english", "انجليزية" -> "English"
- "arabe", "لغة عربية" -> "Arabic language"

**Educational Levels:**
- Primary School (Years 1-5): 1AP, 2AP, 3AP, 4AP, 5AP
- Middle School (Years 1-4): 1AM, 2AM, 3AM, 4AM (BEM)
- High School (Years 1-3): 1AS, 2AS, 3AS (BAC)
- University ESI:
  - 1CP (Sem 1&2): Includes ALG1, ANA1, ALSDS, ARCHI1, SYS1, ELECT, BWEB, TEE, ANA2, ALG2, SYS2, ALSDD, ELECF1, MECA, TEO.
  - 2CP (Sem 1&2): Includes ALG3, ANA3, SFSD, ARCHI2, PRST1, ELECF2, ECON, ANA4, PRST2, POO, OOE, SINF, LOGM.
  - 1CS, 2CS, 3CS (PFE)

**Normalization Rules:**
1.  **EXTRACT FULL NAMES**: If the query contains a person's name (e.g., "Abdellaoui Sidali", "Mr. Ahmed", "Sarah"), assign it to `full_name`.
2.  **USE ELIMINATION**: If a word is not a City, not a Subject, and not a Level, it is likely a Name. Be logical.
3.  **MAP SUBJECTS & LEVELS**: Use the mapping tables above. For university subjects, if the level (e.g., "1CP") is mentioned with a general subject (e.g., "algebra"), you MUST map it to the specific code (e.g., "ALG1"). If no level is mentioned, use the general name (e.g., "Algebra").
4.  **CITIES**: Map Algerian city names to `postal_address` in ENGLISH (e.g., "Alger", "Oran", "Blida").

YOUR JOB:
Analyze the user input and classify EVERY word/phrase into the correct field using the rules above.

**NAME DETECTION RULES (very important):**
- Arabic names like: Mohamed, Ahmed, Sidali, Abdellaoui, Youcef, Amira, etc. -> `full_name`
- French names like: Pierre, Marie, Jean, etc. -> `full_name`
- If input contains 2-3 capitalized words that are not subjects/cities -> likely a full name -> `full_name`
- "teacher X" or "prof X" -> X is the name
- "abdellaoui sidali" -> `full_name`: "Abdellaoui Sidali"

Output JSON Format (REQUIRED - Return ONLY valid JSON, no conversational text):
{{
    "type": "teacher",
    "full_name": "Extracted Name or null",
    "subject": "Normalized Subject Name or Code or null",
    "teaching_level": "Level Code (e.g. 1CP, 3AS, 4AM) or null",
    "postal_address": "City Name (e.g. Alger) or null",
    "education_mode": "online" | "onsite" | null,
    "price_operator": ">" | "<" | ">=" | "<=" | null,
    "price_value": null
}}

User Input: "{query}"

Return ONLY the JSON object. No markdown, no explanation, no extra text."""

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost", # Recommended by OpenRouter
            "X-Title": "Tutoratup Backend"      # Recommended by OpenRouter
        }
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "top_p": 0.8,
            "max_tokens": 300,
            "response_format": { "type": "json_object" } # Request JSON output
        }

        response = requests.post(OPENROUTER_API_URL, json=payload, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()
            
            if "choices" in data and len(data["choices"]) > 0:
                message_content = data["choices"][0]["message"]["content"]
                try:
                    extracted = json.loads(message_content)
                    return normalize_extracted_criteria(extracted, query)
                except json.JSONDecodeError:
                    print("DEBUG: Failed to parse OpenRouter JSON response. Using local fallback.")

        elif response.status_code == 429:
            print("WARN: OpenRouter API rate limited. Using local fallback.")
        elif response.status_code in [401, 403]:
            print("WARN: OpenRouter API key invalid or unauthorized. Using local fallback.")
        else:
            print(f"WARN: OpenRouter API returned status {response.status_code}: {response.text}. Using local fallback.")

    except requests.Timeout:
        print("WARN: OpenRouter API request timed out. Using local fallback.")
    except Exception as e:
        print(f"DEBUG: OpenRouter API error: {str(e)}. Using local fallback.")

    print("INFO: Falling back to local pattern matching.")
    return local_keyword_extraction(query)
