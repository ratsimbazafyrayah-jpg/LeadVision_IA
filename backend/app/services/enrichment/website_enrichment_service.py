from typing import Any, Dict

import httpx


class WebsiteEnrichmentService:
    """
    Service de récupération du contenu d'un site web réel.

    Cette couche ne génère aucune donnée métier.
    Elle récupère uniquement le contenu réellement disponible
    depuis l'URL fournie.
    """

    DEFAULT_TIMEOUT = 20.0

    def __init__(
        self,
        http_client: Any,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        if http_client is None:
            raise TypeError("http_client est requis.")

        if timeout <= 0:
            raise ValueError("Le délai d'attente doit être positif.")

        self.http_client = http_client
        self.timeout = timeout

    def fetch(
        self,
        website: str,
    ) -> Dict[str, Any]:
        if not isinstance(website, str) or not website.strip():
            raise ValueError("L'URL du site web est requise.")

        url = website.strip()

        try:
            response = self.http_client.get(
                url,
                timeout=self.timeout,
                follow_redirects=True,
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "La récupération du site web a dépassé le délai d'attente."
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                "Le site web a retourné une erreur HTTP."
            ) from exc
        except httpx.RequestError as exc:
            raise RuntimeError(
                "Le site web est indisponible."
            ) from exc

        content = response.text

        if not isinstance(content, str):
            raise ValueError(
                "Le contenu retourné par le site web est invalide."
            )

        final_url = str(response.url)

        return {
            "website": url,
            "final_url": final_url,
            "status_code": response.status_code,
            "content_type": response.headers.get("content-type"),
            "html": content,
        }

    @staticmethod
    def extract_emails(html: str) -> list[str]:
        if not isinstance(html, str):
            raise ValueError("Le contenu HTML est requis.")

        import re
        from html import unescape

        pattern = re.compile(
            r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"
        )

        decoded_html = unescape(html)

        emails = []
        seen = set()

        for match in pattern.finditer(decoded_html):
            email = match.group(0).strip().lower()

            if email not in seen:
                seen.add(email)
                emails.append(email)

        return emails

    @staticmethod
    def extract_phones(html: str) -> list[str]:
        if not isinstance(html, str):
            raise ValueError("Le contenu HTML est requis.")

        import re
        from html import unescape

        decoded_html = unescape(html)

        tel_numbers = re.findall(
            r'(?i)tel:\s*([^"\'<>\s]+)',
            decoded_html,
        )

        text_numbers = re.findall(
            r'(?<![\d])\+?[0-9][0-9\s().-]{6,}[0-9](?![\d])',
            decoded_html,
        )

        candidates = [*text_numbers, *tel_numbers]

        phones = []
        seen = set()

        for candidate in candidates:
            phone = candidate.strip()

            if phone.lower().startswith("tel:"):
                phone = phone[4:].strip()

            if phone not in seen:
                seen.add(phone)
                phones.append(phone)

        return phones

    @staticmethod
    def extract_social_links(html: str) -> Dict[str, list[str]]:
        if not isinstance(html, str):
            raise ValueError("Le contenu HTML est requis.")

        from html.parser import HTMLParser
        from urllib.parse import urlparse

        class LinkParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.links = []

            def handle_starttag(self, tag, attrs):
                if tag.lower() != "a":
                    return

                for name, value in attrs:
                    if name.lower() == "href" and isinstance(value, str):
                        self.links.append(value.strip())

        parser = LinkParser()
        parser.feed(html)
        parser.close()

        platforms = {
            "facebook": [],
            "instagram": [],
            "linkedin": [],
            "x": [],
            "youtube": [],
        }

        domains = {
            "facebook": {"facebook.com", "www.facebook.com"},
            "instagram": {"instagram.com", "www.instagram.com"},
            "linkedin": {"linkedin.com", "www.linkedin.com"},
            "x": {
                "x.com",
                "www.x.com",
                "twitter.com",
                "www.twitter.com",
            },
            "youtube": {"youtube.com", "www.youtube.com"},
        }

        seen = {
            platform: set()
            for platform in platforms
        }

        for link in parser.links:
            if not link:
                continue

            parsed = urlparse(link)

            if parsed.scheme not in ("http", "https"):
                continue

            hostname = (parsed.hostname or "").lower()

            for platform, allowed_domains in domains.items():
                if hostname in allowed_domains and link not in seen[platform]:
                    seen[platform].add(link)
                    platforms[platform].append(link)
                    break

        return platforms

    def enrich(self, website: str) -> Dict[str, Any]:
        fetched = self.fetch(website)

        html = fetched["html"]

        return {
            "website": fetched["website"],
            "final_url": fetched["final_url"],
            "status_code": fetched["status_code"],
            "content_type": fetched["content_type"],
            "emails": self.extract_emails(html),
            "phones": self.extract_phones(html),
            "social_links": self.extract_social_links(html),
        }

    def close(self) -> None:
        close = getattr(self.http_client, "close", None)

        if callable(close):
            close()
