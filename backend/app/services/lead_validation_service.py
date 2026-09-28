import re
from urllib.parse import urlparse

from app.database.mongodb import db


leads_collection = db["leads"]


def normalize_text(value):
    if not value:
        return None

    return " ".join(value.strip().split())


def normalize_email(value):
    if not value:
        return None

    return value.strip().lower()


def normalize_url(value):
    if not value:
        return None

    value = value.strip()

    if not value.startswith(("http://", "https://")):
        value = "https://" + value

    return value


def validate_email(email):
    if not email:
        return True

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return bool(re.match(pattern, email))


def validate_url(url):
    if not url:
        return True

    try:
        parsed = urlparse(url)

        return (
            parsed.scheme in ("http", "https")
            and bool(parsed.netloc)
        )

    except Exception:
        return False

def validate_phone(phone):
    if not phone:
        return True

    numbers = re.split(r"\s*(?:/|,|;)\s*", phone.strip())
    pattern = r"^\+?[0-9]{7,15}$"

    for number in numbers:
        cleaned = re.sub(r"[\s\-\(\)]", "", number)
        if not cleaned or not re.match(pattern, cleaned):
            return False

    return True

def validate_social_media(social_media):
    if not social_media:
        return {
            "valid": [],
            "invalid": []
        }

    valid = []
    invalid = []

    if not isinstance(social_media, dict):
        return {
            "valid": [],
            "invalid": ["social_media"]
        }

    for platform, url in social_media.items():

        if not platform:
            continue

        if validate_url(url):
            valid.append(platform)
        else:
            invalid.append(platform)

    return {
        "valid": valid,
        "invalid": invalid
    }

    
def find_duplicate_lead(
    email=None,
    website=None,
    company_name=None,
    city=None
):
    conditions = []

    if email:
        conditions.append({
            "email": normalize_email(email)
        })

    if website:
        conditions.append({
            "website": normalize_url(website)
        })

    if company_name and city:
        conditions.append({
            "company_name": normalize_text(company_name),
            "city": normalize_text(city)
        })

    if not conditions:
        return None

    return leads_collection.find_one({
        "$or": conditions
    })
