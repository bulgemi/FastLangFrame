import pytest
import httpx

@pytest.mark.asyncio
async def test_nginx_oidc_proxy_token():
    """
    Verify that Nginx is proxying /api/oidc/token.
    """
    url = "https://127.0.0.1:8000/api/oidc/token"
    async with httpx.AsyncClient(verify=False) as client:
        # Use POST for token endpoint
        response = await client.post(url)
        # Should return 401 or 400 (from Authelia), but NOT 404/502 (from Nginx)
        assert response.status_code not in [404, 502]

@pytest.mark.asyncio
async def test_authelia_cors_headers_via_proxy():
    """
    Verify that when calling via Proxy, we don't even need CORS because it's Same-Origin.
    But we test that the proxy returns SOMETHING from Authelia.
    """
    url = "https://127.0.0.1:8000/api/oidc/authorization"
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url)
        # Authelia returns error (missing client_id) but it's PROXIED
        assert response.status_code != 404
