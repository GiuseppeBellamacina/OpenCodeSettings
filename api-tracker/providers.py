"""
Provider usage checkers.
Each function returns a dict with:
  - provider: str
  - status: "ok" | "error" | "no_api"
  - usage: float | None (USD spent or credits used)
  - limit: float | None (USD limit or credit limit)
  - remaining: float | None
  - details: dict (provider-specific extra info)
  - error: str | None
"""

import json
import os
from pathlib import Path
from typing import Any

import httpx

TIMEOUT = 10
BROWSER_AUTH_PATH = Path(__file__).resolve().parent / "browser_auth.json"


def _result(provider: str, **kwargs) -> dict[str, Any]:
    base = {
        "provider": provider,
        "status": "ok",
        "usage": None,
        "limit": None,
        "remaining": None,
        "details": {},
        "error": None,
        "dashboard_url": None,
    }
    base.update(kwargs)
    return base


# ── OpenRouter ──────────────────────────────────────────────
def check_openrouter(api_key: str) -> dict:
    try:
        r = httpx.get(
            "https://openrouter.ai/api/v1/auth/key",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        data = r.json().get("data", {})
        usage = data.get("usage", 0)
        limit = data.get("limit")
        remaining = (limit - usage) if limit else None
        return _result(
            "OpenRouter",
            usage=usage,
            limit=limit,
            remaining=remaining,
            dashboard_url="https://openrouter.ai/settings/profile",
            details={
                "label": data.get("label", ""),
                "limit_remaining": data.get("limit_remaining"),
            },
        )
    except Exception as e:
        return _result(
            "OpenRouter",
            status="error",
            error=str(e),
            dashboard_url="https://openrouter.ai/settings/profile",
        )


# ── Groq ────────────────────────────────────────────────────
def check_groq(api_key: str) -> dict:
    # Groq doesn't have a public usage API; we verify the key is valid
    try:
        r = httpx.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        models = r.json().get("data", [])
        return _result(
            "Groq",
            status="ok",
            dashboard_url="https://console.groq.com/settings/usage",
            details={"models_available": len(models), "note": "No usage API"},
        )
    except Exception as e:
        return _result(
            "Groq",
            status="error",
            error=str(e),
            dashboard_url="https://console.groq.com/settings/usage",
        )


# ── Cerebras ────────────────────────────────────────────────
def check_cerebras(api_key: str) -> dict:
    try:
        r = httpx.get(
            "https://api.cerebras.ai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        models = r.json().get("data", [])
        return _result(
            "Cerebras",
            status="ok",
            dashboard_url="https://cloud.cerebras.ai/platform/",
            details={"models_available": len(models), "note": "No usage API"},
        )
    except Exception as e:
        return _result(
            "Cerebras",
            status="error",
            error=str(e),
            dashboard_url="https://cloud.cerebras.ai/platform/",
        )


# ── Google AI Studio ────────────────────────────────────────
def check_google(api_key: str) -> dict:
    try:
        r = httpx.get(
            f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        models = r.json().get("models", [])
        return _result(
            "Google AI Studio",
            status="ok",
            dashboard_url="https://aistudio.google.com/usage",
            details={"models_available": len(models), "note": "No usage API"},
        )
    except Exception as e:
        return _result(
            "Google AI Studio",
            status="error",
            error=str(e),
            dashboard_url="https://aistudio.google.com/usage",
        )


# ── Mistral ─────────────────────────────────────────────────
def check_mistral(api_key: str) -> dict:
    try:
        r = httpx.get(
            "https://api.mistral.ai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        models = r.json().get("data", [])
        return _result(
            "Mistral",
            status="ok",
            dashboard_url="https://console.mistral.ai/codestral?profile_dialog=api-keys",
            details={"models_available": len(models), "note": "No usage API"},
        )
    except Exception as e:
        return _result(
            "Mistral",
            status="error",
            error=str(e),
            dashboard_url="https://console.mistral.ai/codestral?profile_dialog=api-keys",
        )


# ── NVIDIA NIM ──────────────────────────────────────────────
def check_nvidia(api_key: str) -> dict:
    try:
        r = httpx.get(
            "https://integrate.api.nvidia.com/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        models = r.json().get("data", [])
        return _result(
            "NVIDIA",
            status="ok",
            dashboard_url="https://build.nvidia.com/settings/api-keys",
            details={"models_available": len(models), "note": "No usage API"},
        )
    except Exception as e:
        return _result(
            "NVIDIA",
            status="error",
            error=str(e),
            dashboard_url="https://build.nvidia.com/settings/api-keys",
        )


# ── Cloudflare Workers AI ──────────────────────────────────
def check_cloudflare(api_key: str) -> dict:
    dashboard_url = "https://dash.cloudflare.com/?to=/:account/ai/workers-ai"
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
    try:
        # Verify token first
        r = httpx.get(
            "https://api.cloudflare.com/client/v4/user/tokens/verify",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        success = data.get("success", False)
        if not success:
            return _result(
                "Cloudflare Workers AI",
                status="error",
                dashboard_url=dashboard_url,
                details={"note": "Token invalid"},
            )

        token_status = data.get("result", {}).get("status", "unknown")
        details = {"token_status": token_status}

        # If account_id available, try to get AI usage from billing
        if account_id:
            try:
                r2 = httpx.get(
                    f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/runs/summary",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=TIMEOUT,
                )
                if r2.status_code == 200:
                    ai_data = r2.json().get("result", {})
                    details["total_runs"] = ai_data.get("total_count")
                    details["note"] = "AI runs summary loaded"
                else:
                    details["note"] = "Token active · Usage via dashboard"
            except Exception:
                details["note"] = "Token active · Usage via dashboard"
        else:
            details["note"] = "Add CLOUDFLARE_ACCOUNT_ID for usage data"

        return _result(
            "Cloudflare Workers AI",
            status="ok",
            dashboard_url=dashboard_url,
            details=details,
        )
    except Exception as e:
        return _result(
            "Cloudflare Workers AI",
            status="error",
            error=str(e),
            dashboard_url=dashboard_url,
        )


# ── Sambanova ───────────────────────────────────────────────
def check_sambanova(api_key: str) -> dict:
    try:
        r = httpx.get(
            "https://api.sambanova.ai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        models = r.json().get("data", [])
        return _result(
            "Sambanova",
            status="ok",
            dashboard_url="https://cloud.sambanova.ai/apis",
            details={"models_available": len(models), "note": "No usage API"},
        )
    except Exception as e:
        return _result(
            "Sambanova",
            status="error",
            error=str(e),
            dashboard_url="https://cloud.sambanova.ai/apis",
        )


# ── ZAI (Zhipu) ────────────────────────────────────────────
def check_zai(api_key: str) -> dict:
    try:
        r = httpx.get(
            "https://open.bigmodel.cn/api/paas/v4/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return _result(
            "ZAI (Zhipu)",
            status="ok",
            dashboard_url="https://z.ai/manage-apikey/apikey-list",
            details={"note": "No usage API"},
        )
    except Exception as e:
        return _result(
            "ZAI (Zhipu)",
            status="error",
            error=str(e),
            dashboard_url="https://z.ai/manage-apikey/apikey-list",
        )


# ── Scaleway ───────────────────────────────────────────────
def check_scaleway(api_key: str) -> dict:
    dashboard_url = "https://console.scaleway.com/iam/users"
    try:
        r = httpx.get(
            "https://api.scaleway.ai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        models = r.json().get("data", r.json().get("models", []))
        count = len(models) if isinstance(models, list) else 0
        return _result(
            "Scaleway",
            status="ok",
            dashboard_url=dashboard_url,
            details={"models_available": count, "note": "No usage API"},
        )
    except Exception:
        # Fallback: try Generative APIs endpoint
        try:
            r2 = httpx.get(
                "https://api.scaleway.ai/v1beta1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=TIMEOUT,
            )
            r2.raise_for_status()
            return _result(
                "Scaleway",
                status="ok",
                dashboard_url=dashboard_url,
                details={"note": "Key valid · No usage API"},
            )
        except Exception as e:
            return _result(
                "Scaleway", status="error", error=str(e), dashboard_url=dashboard_url
            )


# ── OpenCode Zen ───────────────────────────────────────────
def check_opencode(api_key: str) -> dict:
    dashboard_url = "https://opencode.ai/it/zen"
    try:
        r = httpx.get(
            "https://opencode.ai/api/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        models = r.json().get("data", [])
        count = len(models) if isinstance(models, list) else 0
        return _result(
            "OpenCode Zen",
            status="ok",
            dashboard_url=dashboard_url,
            details={"models_available": count, "note": "No usage API"},
        )
    except Exception:
        # Even if models endpoint fails, key format looks valid
        if api_key.startswith("sk-"):
            return _result(
                "OpenCode Zen",
                status="ok",
                dashboard_url=dashboard_url,
                details={"note": "Key format valid · No usage API"},
            )
        return _result(
            "OpenCode Zen",
            status="error",
            error="Could not validate key",
            dashboard_url=dashboard_url,
        )


# ── GitHub ─────────────────────────────────────────────────
def check_github(token: str) -> dict:
    try:
        r = httpx.get(
            "https://api.github.com/rate_limit",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        data = r.json().get("rate", {})
        limit = data.get("limit", 0)
        remaining = data.get("remaining", 0)
        used = data.get("used", 0)
        return _result(
            "GitHub",
            usage=used,
            limit=limit,
            remaining=remaining,
            dashboard_url="https://github.com/settings/billing",
            details={"reset": data.get("reset")},
        )
    except Exception as e:
        return _result(
            "GitHub",
            status="error",
            error=str(e),
            dashboard_url="https://github.com/settings/billing",
        )


# ── GitHub Copilot ─────────────────────────────────────────
def _load_browser_auth(provider_key: str) -> dict | None:
    """Load browser auth config from browser_auth.json."""
    try:
        with open(BROWSER_AUTH_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data.get(provider_key)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def check_github_copilot(_unused: str = "") -> dict:
    dashboard_url = "https://github.com/settings/copilot"
    auth = _load_browser_auth("github_copilot")
    if not auth:
        return _result(
            "GitHub Copilot",
            status="error",
            error="browser_auth.json mancante o sezione github_copilot non trovata",
            dashboard_url=dashboard_url,
        )

    cookies = auth.get("cookies", {})
    headers = auth.get("headers", {})
    url = auth.get("url", "https://github.com/github-copilot/chat/entitlement")

    # Check if cookies are still placeholder
    session = cookies.get("user_session", "")
    if not session or session.startswith("YOUR_"):
        return _result(
            "GitHub Copilot",
            status="error",
            error="Configura user_session in browser_auth.json",
            dashboard_url=dashboard_url,
        )

    # Build cookie string
    cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())

    try:
        r = httpx.get(
            url,
            headers={
                **headers,
                "cookie": cookie_str,
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            },
            timeout=TIMEOUT,
            follow_redirects=True,
        )
        r.raise_for_status()
        data = r.json()

        quotas = data.get("quotas", {})
        token_based = quotas.get("tokenBasedBillingEnabled", False)
        premium_quota = quotas.get("premiumInteractionsQuota", {})
        premium_unlimited = premium_quota.get("unlimited", False)

        if token_based or premium_unlimited:
            # New AI-credits / token-based billing system — no request counts
            return _result(
                "GitHub Copilot",
                usage=None,
                limit=None,
                remaining=None,
                dashboard_url=dashboard_url,
                details={
                    "plan": data.get("plan", "unknown"),
                    "license": data.get("licenseType", "unknown"),
                    "reset_date": quotas.get("resetDate"),
                    "overages": quotas.get("overagesEnabled"),
                    "overage_permitted": quotas.get("overageQuota", {}).get("permitted", False),
                    "premium_pct_remaining": premium_quota.get("percentRemaining", 100.0),
                    "token_based": True,
                    "copilot_scale": True,
                },
            )

        # Legacy request-based billing
        limits = quotas.get("limits", {})
        remaining_data = quotas.get("remaining", {})

        premium_limit = limits.get("premiumInteractions", 300)
        premium_remaining = remaining_data.get("premiumInteractions", 0)
        premium_used = premium_limit - premium_remaining

        # Custom scale: 100% every 300 requests, max 767%
        MAX_PCT = 767.2
        absolute_max = int(premium_limit * MAX_PCT / 100)
        custom_pct = (
            min((premium_used / premium_limit) * 100, MAX_PCT) if premium_limit else 0
        )
        remaining_to_cap = max(absolute_max - premium_used, 0)

        return _result(
            "GitHub Copilot",
            usage=premium_used,
            limit=premium_limit,
            remaining=remaining_to_cap,
            dashboard_url=dashboard_url,
            details={
                "plan": data.get("plan", "unknown"),
                "license": data.get("licenseType", "unknown"),
                "reset_date": quotas.get("resetDate"),
                "overages": quotas.get("overagesEnabled"),
                "custom_pct": round(custom_pct, 1),
                "absolute_max": absolute_max,
                "copilot_scale": True,
            },
        )
    except Exception as e:
        return _result(
            "GitHub Copilot", status="error", error=str(e), dashboard_url=dashboard_url
        )


# ── Registry ──────────────────────────────────────────────
PROVIDERS = {
    "NVIDIA": check_nvidia,
    "GROQ": check_groq,
    "CEREBRAS": check_cerebras,
    "GOOGLE_AI_STUDIO": check_google,
    "GITHUB_TOKEN": check_github,
    "MISTRAL_LP": check_mistral,
    "CLOUDFLARE_WORKERS_AI": check_cloudflare,
    "OPENROUTER": check_openrouter,
    "SAMBANOVA": check_sambanova,
    "ZAI": check_zai,
    "SCALEWAY": check_scaleway,
    "OPENCODE_ZEN": check_opencode,
}

# Providers that use browser_auth.json instead of env vars
BROWSER_PROVIDERS = [
    check_github_copilot,
]


def check_all() -> list[dict]:
    """Check all providers using keys from environment variables."""
    results = []
    for env_var, checker in PROVIDERS.items():
        key = os.environ.get(env_var, "")
        if not key or key.startswith("bla_") or key.endswith("?"):
            results.append(
                _result(
                    checker.__name__.replace("check_", "").title(),
                    status="no_api",
                    details={"note": "Key not configured"},
                )
            )
            continue
        results.append(checker(key))

    # Browser-auth providers (no env var needed)
    for checker in BROWSER_PROVIDERS:
        results.append(checker())

    return results
