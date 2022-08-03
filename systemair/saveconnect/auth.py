import time
import httpx
from bs4 import BeautifulSoup


class SaveConnectAuth:

    def __init__(self, loop):
        """HTTP Client"""
        # self._cookie_jar = aiohttp.CookieJar(unsafe=True)
        self._client: httpx.AsyncClient = httpx.AsyncClient()
        self._oidc_token: dict = {}
        self.loop = loop

        self._token_expiry = time.time()

    async def auth(self, email, password):
        auth_url = (
            "{authorization-endpoint}?client_id={client-id}&response_type={response_type}&redirect_uri={redirect-uri}"
            "&scope={scope}&state={state}"
        ).format(**{
            "authorization-endpoint": "https://sso.systemair.com/auth/realms/iot/protocol/openid-connect/auth",
            "client-id": "iot-application",
            "response_type": "code",
            "redirect-uri": "https://homesolutions.systemair.com",
            "scope": "openid email profile",
            "state": "xyzABC123"
        })

        response = await self._client.get(auth_url, follow_redirects=True)

        soup = BeautifulSoup(response.content, features="html.parser")

        login_form_action = soup.find("form", {
            "id": "kc-form-login"
        })["action"]

        response = await self._client.post(login_form_action, data=dict(
            username=email,
            password=password,
            rememberMe="on",
            credentialId=""
        ), follow_redirects=True)
        code = response.url.params.get("code")

        # Get Access Token With Code
        response = await self._client.post(
            url="https://sso.systemair.com/auth/realms/iot/protocol/openid-connect/token",
            headers={
                "content-type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "authorization_code",
                "client_id": "iot-application",
                "code": code,
                "redirect_uri": "https://homesolutions.systemair.com"
            }
        )

        self._oidc_token = response.json()

        return True if self._oidc_token else False

    async def refresh_token(self):
        response = await self._client.post(
            url="https://sso.systemair.com/auth/realms/iot/protocol/openid-connect/token",
            headers={
                "content-type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "refresh_token",
                "client_id": "iot-application",
                "refresh_token": self._oidc_token["refresh_token"],
                "redirect_uri": "https://homesolutions.systemair.com"
            }
        )
        self._oidc_token = response.json()

        self._token_expiry = time.time() + self._oidc_token["expires_in"] - (self._oidc_token["expires_in"] * .20)

    def is_auth(self):
        return self._token_expiry < time.time() and len(self._oidc_token) > 0

    @property
    def token(self):
        return self._oidc_token

    @token.setter
    def token(self, token):
        self._oidc_token = token
