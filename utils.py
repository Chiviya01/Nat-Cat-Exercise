import ast
import re
import unicodedata
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from tqdm import tqdm
import spacy
from transformers import pipeline
import pycountry
import pycountry_convert as pc
import tldextract

tqdm.pandas()

# ──────────────────────────────────────────────────────────────────────────────
# DOMAIN & URL FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def extract_domain_parts(domain: str) -> pd.Series:
    """
    Splits a domain into subdomain, domain root, and top-level domain (TLD).
    """
    domain = domain.split()[0].strip()
    extracted = tldextract.extract(domain)
    return pd.Series({
        'subdomain': extracted.subdomain,
        'domain_root': extracted.domain,
        'tld': extracted.suffix
    })

def is_url_accessible(url: str) -> bool:
    """
    Checks if a given URL is accessible via a HEAD request.
    """
    try:
        response = requests.head(url, timeout=5)
        return response.status_code < 400
    except:
        return False

def get_best_title_from_url(url: str) -> str:
    """
    Fetches a URL and returns the longest valid <title> or header tag (h1–h3).
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            candidates = []

            if soup.title and soup.title.text:
                candidates.append(soup.title.text.strip())

            for tag in ['h1', 'h2', 'h3']:
                for header in soup.find_all(tag):
                    text = header.get_text(strip=True)
                    if text:
                        candidates.append(text)

            candidates = [c for c in candidates if c.strip()]
            if candidates:
                return max(candidates, key=len)
    except Exception:
        return None
    return None

# ──────────────────────────────────────────────────────────────────────────────
# TEXT CLEANING FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def normalize_unicode(text: str) -> str:
    """
    Converts non-ASCII unicode characters to closest ASCII equivalents.
    """
    if not isinstance(text, str):
        return ""
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")

def clean_title(text: str) -> str:
    """
    Cleans a title by removing non-ASCII characters and normalizing punctuation/spacing.
    """
    if not isinstance(text, str):
        return ""
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    text = re.sub(r'[^a-zA-Z0-9\s.,:;!?\'\"-]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ──────────────────────────────────────────────────────────────────────────────
# KEYWORD & LOCATION PROCESSING
# ──────────────────────────────────────────────────────────────────────────────

def extract_keywords(text: str) -> list:
    """
    Extracts top keywords from a title using a keyword extractor.
    Assumes kw_extractor is defined globally.
    """
    keywords = kw_extractor.extract_keywords(text)
    return [kw for kw, score in keywords]

def location_list_to_string(x) -> str:
    """
    Converts a list of locations (or stringified list) into a single space-separated string.
    """
    if isinstance(x, list):
        return " ".join(x)
    elif isinstance(x, str):
        try:
            parsed = ast.literal_eval(x)
            if isinstance(parsed, list):
                return " ".join(parsed)
        except (ValueError, SyntaxError):
            return x
    return ""

def get_country_from_text(text: str) -> str:
    """
    Attempts to extract a valid country name from text using pycountry lookup.
    """
    if not isinstance(text, str):
        return None
    words = text.split()
    for word in reversed(words):
        try:
            match = pycountry.countries.lookup(word)
            return match.name
        except LookupError:
            continue
    return None

def get_continent(country_name: str) -> str:
    """
    Maps a country name to its continent using pycountry-convert.
    """
    try:
        country = pycountry.countries.lookup(country_name)
        alpha2 = country.alpha_2
        continent_code = pc.country_alpha2_to_continent_code(alpha2)
        return pc.convert_continent_code_to_continent_name(continent_code)
    except:
        return 'Unknown'
