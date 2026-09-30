import httpx
import pytest

from app.services.enrichment.website_enrichment_service import (
    WebsiteEnrichmentService,
)


class FakeResponse:
    def __init__(
        self,
        text="",
        url="https://example.com",
        status_code=200,
        headers=None,
        error=None,
    ):
        self.text = text
        self.url = url
        self.status_code = status_code
        self.headers = headers or {}
        self.error = error

    def raise_for_status(self):
        if self.error:
            raise self.error


class FakeHttpClient:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.closed = False
        self.last_request = None

    def get(
        self,
        url,
        timeout=None,
        follow_redirects=False,
    ):
        self.last_request = {
            "url": url,
            "timeout": timeout,
            "follow_redirects": follow_redirects,
        }

        if self.error:
            raise self.error

        return self.response

    def close(self):
        self.closed = True


def build_service(client):
    return WebsiteEnrichmentService(
        http_client=client,
        timeout=10.0,
    )


def test_fetch_requires_website():
    service = build_service(FakeHttpClient())

    with pytest.raises(
        ValueError,
        match="URL du site web est requise",
    ):
        service.fetch("")


def test_fetch_maps_real_website_content():
    client = FakeHttpClient(
        response=FakeResponse(
            text="<html><body>Entreprise Réelle</body></html>",
            url="https://example.com/about",
            status_code=200,
            headers={
                "content-type": "text/html; charset=utf-8",
            },
        )
    )

    service = build_service(client)

    result = service.fetch(" https://example.com ")

    assert result == {
        "website": "https://example.com",
        "final_url": "https://example.com/about",
        "status_code": 200,
        "content_type": "text/html; charset=utf-8",
        "html": "<html><body>Entreprise Réelle</body></html>",
    }

    assert client.last_request == {
        "url": "https://example.com",
        "timeout": 10.0,
        "follow_redirects": True,
    }


def test_fetch_timeout_is_converted():
    client = FakeHttpClient(
        error=httpx.ReadTimeout("timeout")
    )

    service = build_service(client)

    with pytest.raises(
        RuntimeError,
        match="dépassé le délai d'attente",
    ):
        service.fetch("https://example.com")


def test_fetch_http_error_is_converted():
    request = httpx.Request(
        "GET",
        "https://example.com",
    )
    response = httpx.Response(
        503,
        request=request,
    )

    client = FakeHttpClient(
        response=FakeResponse(
            error=httpx.HTTPStatusError(
                "service unavailable",
                request=request,
                response=response,
            )
        )
    )

    service = build_service(client)

    with pytest.raises(
        RuntimeError,
        match="erreur HTTP",
    ):
        service.fetch("https://example.com")


def test_fetch_request_error_is_converted():
    client = FakeHttpClient(
        error=httpx.ConnectError("connection failed")
    )

    service = build_service(client)

    with pytest.raises(
        RuntimeError,
        match="indisponible",
    ):
        service.fetch("https://example.com")


def test_close_closes_http_client():
    client = FakeHttpClient()
    service = build_service(client)

    service.close()

    assert client.closed is True

def test_extract_emails_from_html():
    client = FakeHttpClient()
    service = build_service(client)

    html = """
    <html>
        <body>
            Contactez-nous : contact@example.com
            <a href="mailto:info@example.com">Email</a>
        </body>
    </html>
    """

    result = service.extract_emails(html)

    assert result == [
        "contact@example.com",
        "info@example.com",
    ]

def test_extract_emails_normalizes_and_deduplicates():
    client = FakeHttpClient()
    service = build_service(client)

    html = """
    <div>CONTACT@EXAMPLE.COM</div>
    <div>contact@example.com</div>
    <div>info@example.com</div>
    """

    result = service.extract_emails(html)

    assert result == [
        "contact@example.com",
        "info@example.com",
    ]

def test_extract_emails_returns_empty_when_no_email_exists():
    client = FakeHttpClient()
    service = build_service(client)

    html = """
    <html>
        <body>
            <h1>Entreprise réelle</h1>
            <p>Bienvenue sur notre site.</p>
        </body>
    </html>
    """

    result = service.extract_emails(html)

    assert result == []

def test_enrich_website_extracts_emails_from_fetched_html():
    client = FakeHttpClient(
        response=FakeResponse(
            text="""
            <html>
                <body>
                    Contact : contact@example.com
                    <a href="mailto:info@example.com">Email</a>
                </body>
            </html>
            """,
            url="https://example.com",
            status_code=200,
            headers={
                "content-type": "text/html; charset=utf-8",
            },
        )
    )

    service = build_service(client)

    result = service.enrich("https://example.com")

    assert result == {
        "website": "https://example.com",
        "final_url": "https://example.com",
        "status_code": 200,
        "content_type": "text/html; charset=utf-8",
        "emails": [
            "contact@example.com",
            "info@example.com",
        ],
        "phones": [],
        "social_links": {
            "facebook": [],
            "instagram": [],
            "linkedin": [],
            "x": [],
            "youtube": [],
        },
    }

def test_extract_phones_from_html():
    client = FakeHttpClient()
    service = build_service(client)

    html = """
    <html>
        <body>
            Téléphone : +261 20 22 642 33
            <a href="tel:+26120248642">Appelez-nous</a>
        </body>
    </html>
    """

    result = service.extract_phones(html)

    assert result == [
        "+261 20 22 642 33",
        "+26120248642",
    ]

def test_extract_social_links_from_html():
    client = FakeHttpClient()
    service = build_service(client)

    html = """
    <html>
        <body>
            <a href="https://facebook.com/example">Facebook</a>
            <a href="https://www.instagram.com/example">Instagram</a>
            <a href="https://www.linkedin.com/company/example">LinkedIn</a>
            <a href="https://x.com/example">X</a>
            <a href="https://twitter.com/example">Twitter</a>
            <a href="https://youtube.com/@example">YouTube</a>
            <a href="https://facebook.com/example">Facebook</a>
        </body>
    </html>
    """

    result = service.extract_social_links(html)

    assert result == {
        "facebook": [
            "https://facebook.com/example",
        ],
        "instagram": [
            "https://www.instagram.com/example",
        ],
        "linkedin": [
            "https://www.linkedin.com/company/example",
        ],
        "x": [
            "https://x.com/example",
            "https://twitter.com/example",
        ],
        "youtube": [
            "https://youtube.com/@example",
        ],
    }

def test_enrich_website_returns_all_extracted_contacts():
    client = FakeHttpClient(
        response=FakeResponse(
            text="""
            <html>
                <body>
                    Contact : contact@example.com
                    Téléphone : +261 20 22 642 33
                    <a href="https://facebook.com/example">Facebook</a>
                    <a href="https://www.instagram.com/example">Instagram</a>
                </body>
            </html>
            """,
            url="https://example.com",
            status_code=200,
            headers={
                "content-type": "text/html; charset=utf-8",
            },
        )
    )

    service = build_service(client)

    result = service.enrich("https://example.com")

    assert result == {
        "website": "https://example.com",
        "final_url": "https://example.com",
        "status_code": 200,
        "content_type": "text/html; charset=utf-8",
        "emails": [
            "contact@example.com",
        ],
        "phones": [
            "+261 20 22 642 33",
        ],
        "social_links": {
            "facebook": [
                "https://facebook.com/example",
            ],
            "instagram": [
                "https://www.instagram.com/example",
            ],
            "linkedin": [],
            "x": [],
            "youtube": [],
        },
    }


def test_extract_phones_ignores_dates():
    client = FakeHttpClient()
    service = build_service(client)

    html = """
    <html>
        <body>
            Mise à jour : 2024-09-09
            Téléphone : +261 20 22 642 33
        </body>
    </html>
    """

    result = service.extract_phones(html)

    assert result == [
        "+261 20 22 642 33",
    ]

def test_extract_phones_ignores_numeric_fragments_and_dates():
    client = FakeHttpClient()
    service = build_service(client)

    html = """
    <html>
        <body>
            Coordonnées internes : 2.0.19.12
            Donnée : 224) 100
            Donnée : 130) 100
            Mise à jour : 2025-02-06 12
            Téléphone : +261 34 01 077 71
        </body>
    </html>
    """

    result = service.extract_phones(html)

    assert result == [
        "+261 34 01 077 71",
    ]
