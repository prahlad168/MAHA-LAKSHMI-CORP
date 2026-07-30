#!/usr/bin/env python3
"""
MAHA SALES ENGINE V1 - Gumroad Connectivity Verification
Reads GUMROAD_API_KEY from environment only.
Does NOT publish any product.
"""

import os
import sys
import json
import time
import logging
from typing import Dict, Any

logger = logging.getLogger("maha-sales-engine.marketplace_connector.connectivity_check")


def check_configuration() -> Dict[str, Any]:
    api_key = os.getenv("GUMROAD_API_KEY", "").strip()
    return {
        "configured": bool(api_key),
        "source": "environment",
        "key_present": bool(api_key),
        "key_length": len(api_key) if api_key else 0
    }


async def verify_connectivity() -> Dict[str, Any]:
    config = check_configuration()

    if not config["configured"]:
        return {
            "success": False,
            "configuration_status": "missing",
            "authentication_status": "not_attempted",
            "http_status": None,
            "account_verified": False,
            "error": "GUMROAD_API_KEY is missing from environment",
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

    api_key = os.getenv("GUMROAD_API_KEY", "").strip()
    result = {
        "success": False,
        "configuration_status": "present",
        "authentication_status": "pending",
        "http_status": None,
        "account_verified": False,
        "error": None,
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    try:
        import aiohttp
        import certifi
        import ssl
    except Exception as e:
        result["authentication_status"] = "dependency_missing"
        result["error"] = f"aiohttp/certifi/ssl is required for live connectivity check: {e}"
        return result

    try:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(
                "https://api.gumroad.com/v2/user",
                params={"access_token": api_key},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                result["http_status"] = response.status
                text = await response.text()

                try:
                    data = json.loads(text) if text else {}
                except json.JSONDecodeError:
                    data = {"raw": text}

                if response.status == 200 and data.get("success"):
                    result["success"] = True
                    result["authentication_status"] = "authenticated"
                    result["account_verified"] = True
                    user = data.get("user") or {}
                    result["account"] = {
                        "user_id": user.get("id"),
                        "name": user.get("name"),
                        "email": user.get("email"),
                        "slug": user.get("slug")
                    }
                elif response.status in (401, 403):
                    result["authentication_status"] = "invalid_credentials"
                    result["error"] = data.get("error") or "Unauthorized"
                else:
                    result["authentication_status"] = "failed"
                    result["error"] = data.get("error") or f"HTTP {response.status}"
    except Exception as e:
        result["authentication_status"] = "error"
        result["error"] = str(e)

    return result


def main() -> int:
    print("Gumroad Connectivity Verification")
    print("Source: environment variable GUMROAD_API_KEY only")
    print("-" * 60)

    config = check_configuration()
    print(f"Configuration status: {config['configured']}")
    print(f"Key present: {config['key_present']}")

    if not config["configured"]:
        print("-" * 60)
        print("Result: configuration_error")
        print("Action: set GUMROAD_API_KEY in environment")
        return 2

    result = __import__("asyncio").run(verify_connectivity())

    print(f"Authentication status: {result['authentication_status']}")
    print(f"HTTP status: {result['http_status']}")
    print(f"Account verified: {result['account_verified']}")
    if result.get("account"):
        account = result["account"]
        print(f"Account: {account.get('name')} / {account.get('slug')}")
    if result.get("error"):
        print(f"Error: {result['error']}")
    print("-" * 60)
    print(f"Overall success: {result['success']}")
    print(f"Checked at: {result['checked_at']}")
    
    try:
        import certifi
        import ssl
        print(f"SSL configuration: certifi CA bundle + default SSLContext")
        print(f"certifi path: {certifi.where()}")
        print(f"OpenSSL version: {ssl.OPENSSL_VERSION}")
    except Exception as e:
        print(f"SSL configuration: unavailable ({e})")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
