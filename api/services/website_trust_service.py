from __future__ import annotations

import socket
import ssl
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import requests

SUSPICIOUS_KEYWORDS = {
    "verify", "wallet", "claim", "urgent", "login", "bonus", "free", "airdrop",
    "signin", "secure-update", "reset-password",
}
SUSPICIOUS_TLDS = {"zip", "top", "work", "click", "gq", "country"}
KNOWN_SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "rb.gy"}

try:
    import whois  # type: ignore
except Exception:  # pragma: no cover
    whois = None


class WebsiteTrustService:
    def analyze(self, url: str) -> dict[str, Any]:
        parsed = urlparse(url if "://" in url else f"https://{url}")
        host = parsed.hostname or ""
        explanation: list[str] = []
        trust_score = 100
        redirect_chain: list[str] = []

        if not host:
            return {
                "url": url,
                "trust_score": 0,
                "risk_level": "invalid",
                "explanation": ["The provided URL is invalid or missing a hostname."],
                "recommendations": ["Verify the URL formatting before trusting the site."],
            }

        if host in KNOWN_SHORTENERS:
            trust_score -= 15
            explanation.append("The domain is a URL shortener, which can obscure the final destination.")
        if host.startswith("xn--") or any(ord(ch) > 127 for ch in host):
            trust_score -= 18
            explanation.append("Potential homograph or IDN spoofing characteristics were detected in the hostname.")
        if host.replace(".", "").isdigit():
            trust_score -= 20
            explanation.append("The URL uses a raw IP address instead of a normal domain name.")
        if host.split(".")[-1] in SUSPICIOUS_TLDS:
            trust_score -= 10
            explanation.append("The top-level domain is commonly abused for low-trust campaigns.")
        if any(keyword in url.lower() for keyword in SUSPICIOUS_KEYWORDS):
            trust_score -= 12
            explanation.append("Suspicious marketing or credential-themed keywords were found in the URL.")
        if host.count(".") >= 3:
            trust_score -= 8
            explanation.append("The hostname contains many nested subdomains, which is common in phishing kits.")

        ssl_info = self._get_ssl_info(host)
        if ssl_info["valid"]:
            explanation.append("A TLS certificate was retrieved successfully.")
        else:
            trust_score -= 12
            explanation.append(ssl_info["reason"])

        http_info = self._fetch_http_metadata(parsed.geturl())
        redirect_chain = http_info["redirect_chain"]
        trust_score += http_info["score_adjustment"]
        explanation.extend(http_info["notes"])

        domain_age_days = None
        if whois is not None:
            try:
                w = whois.whois(host)
                created = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
                if created:
                    domain_age_days = max(0, (datetime.now(timezone.utc) - created.astimezone(timezone.utc)).days)
                    if domain_age_days < 30:
                        trust_score -= 20
                        explanation.append("The domain appears to be very new, which increases scam risk.")
                    elif domain_age_days < 180:
                        trust_score -= 8
                        explanation.append("The domain is relatively new and should be treated with caution.")
            except Exception:
                explanation.append("WHOIS age information could not be retrieved.")
        else:
            explanation.append("WHOIS checks are unavailable in the current environment.")

        trust_score = max(0, min(100, trust_score))
        risk_level = "trusted" if trust_score >= 75 else "suspicious" if trust_score >= 45 else "high-risk"
        recommendations = self._build_recommendations(trust_score, redirect_chain, ssl_info["valid"])

        return {
            "url": parsed.geturl(),
            "hostname": host,
            "trust_score": trust_score,
            "risk_level": risk_level,
            "domain_age_days": domain_age_days,
            "ssl": ssl_info,
            "redirect_chain": redirect_chain,
            "explanation": explanation,
            "recommendations": recommendations,
        }

    @staticmethod
    def _get_ssl_info(host: str) -> dict[str, Any]:
        try:
            context = ssl.create_default_context()
            with socket.create_connection((host, 443), timeout=4) as sock:
                with context.wrap_socket(sock, server_hostname=host) as secure_sock:
                    cert = secure_sock.getpeercert()
                    not_after = cert.get("notAfter")
                    issuer = dict(item[0] for item in cert.get("issuer", []))
                    return {
                        "valid": True,
                        "issuer": issuer.get("organizationName"),
                        "not_after": not_after,
                    }
        except Exception as exc:
            return {"valid": False, "reason": f"TLS validation failed or the certificate was unavailable: {exc}"}

    @staticmethod
    def _fetch_http_metadata(url: str) -> dict[str, Any]:
        redirect_chain: list[str] = []
        notes: list[str] = []
        score_adjustment = 0
        try:
            response = requests.get(url, timeout=6, allow_redirects=True, headers={"User-Agent": "DeepShield/1.0"})
            redirect_chain = [resp.url for resp in response.history] + [response.url]
            if len(response.history) >= 3:
                score_adjustment -= 10
                notes.append("The URL redirected through multiple hops before landing.")
            page_text = response.text.lower()[:5000]
            suspicious_terms = sum(keyword in page_text for keyword in SUSPICIOUS_KEYWORDS)
            if suspicious_terms >= 3:
                score_adjustment -= 12
                notes.append("The landing page contains multiple phishing-adjacent keywords.")
            elif suspicious_terms == 0:
                score_adjustment += 2
            if response.status_code >= 400:
                score_adjustment -= 8
                notes.append("The website returned an error response, which reduces trust.")
        except Exception as exc:
            notes.append(f"Live HTTP checks could not be completed: {exc}")
            score_adjustment -= 5
        return {"redirect_chain": redirect_chain, "notes": notes, "score_adjustment": score_adjustment}

    @staticmethod
    def _build_recommendations(trust_score: int, redirect_chain: list[str], ssl_valid: bool) -> list[str]:
        recommendations = []
        if trust_score < 45:
            recommendations.append("Avoid submitting credentials or downloading files from this site until it is independently verified.")
        if not ssl_valid:
            recommendations.append("Do not trust the site for sensitive activity until certificate issues are resolved.")
        if len(redirect_chain) > 2:
            recommendations.append("Inspect the full redirect path before sharing or trusting this URL.")
        if not recommendations:
            recommendations.append("The site shows no immediate critical indicators, but normal due diligence is still recommended.")
        return recommendations


website_trust_service = WebsiteTrustService()
