import re
from urllib.parse import urlparse
import streamlit as st
import tldextract # For robust domain name extraction

def validate_and_format_url(url_string: str) -> str | None:
    """
    Validates a URL and adds 'https://' if no scheme is present.
    Returns formatted URL or None if invalid.
    """
    if not url_string:
        return None
    if not url_string.startswith(('http://', 'https://')):
        url_string = 'https://' + url_string
    
    # Basic regex for URL validation (can be improved for stricter validation)
    # Using validators library would be more robust but this is a simpler approach
    # For this project, we'll rely on Streamlit's input validation and user's correctness primarily
    # and basic check here.
    parsed_url = urlparse(url_string)
    if parsed_url.scheme and parsed_url.netloc:
        return url_string
    st.warning(f"Potentially invalid URL: {url_string}. Please ensure it's correct.")
    return url_string # Return it anyway, let requests handle errors

def extract_company_name_from_url(url: str) -> str:
    """
    Extracts a plausible company name from a URL.
    Example: "https://www.example.com" -> "example"
    """
    if not url:
        return "company"
    try:
        extracted = tldextract.extract(url)
        if extracted.domain:
            return extracted.domain
        # Fallback for unusual URLs or if tldextract fails
        netloc = urlparse(url).netloc
        if netloc:
            parts = netloc.split('.')
            # Handle cases like 'www.example.com' or 'example.co.uk'
            if len(parts) > 1 and parts[0] == 'www':
                return parts[1]
            return parts[0]
    except Exception:
        pass # Ignore errors and fallback
    return "company" # Default fallback

def sanitize_for_filename(text: str) -> str:
    """Sanitizes a string to be used in a filename."""
    text = text.lower()
    text = re.sub(r'\s+', '_', text) # Replace spaces with underscores
    text = re.sub(r'[^\w\-.]', '', text) # Remove non-alphanumeric characters except _ and -
    return text[:50] # Limit length