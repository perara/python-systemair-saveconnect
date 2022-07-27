import httpx
from keycloak import KeycloakOpenID
from bs4 import BeautifulSoup


class SaveConnectAuth:

    def __init__(self):
        """HTTP Client"""
        # self._cookie_jar = aiohttp.CookieJar(unsafe=True)
        self._client: httpx.AsyncClient = httpx.AsyncClient()
        self._oidc_token: dict = {}

    async def auth_openid(self):
        return KeycloakOpenID(server_url="https://sso.systemair.com/auth/",
                              client_id="iot-application",
                              realm_name="iot")

    async def auth(self, email, password):
        # Configure client
        keycloak_openid = await self.auth_openid()

        # Get Code With Oauth Authorization Request
        auth_url = keycloak_openid.auth_url(
            redirect_uri="https://homesolutions.systemair.com",
            scope="openid",
            state="xyzABC123")  # TODO state

        r1 = await self._client.get(auth_url, follow_redirects=True)

        soup = BeautifulSoup(r1.content, features="html.parser")

        login_form = soup.find("form", {
            "id": "kc-form-login"
        })["action"]

        r2 = await self._client.post(login_form, data=dict(
            username=email,
            password=password,
            rememberMe="on",
            credentialId=""
        ), follow_redirects=True)

        # Get Access Token With Code
        self._oidc_token = keycloak_openid.token(
            grant_type='authorization_code',
            code=r2.url.params["code"],
            redirect_uri="https://homesolutions.systemair.com")

        return True if self._oidc_token else False

    async def refresh_token(self):
        keycloak_openid = await self.auth_openid()

        self._oidc_token = keycloak_openid.refresh_token(
            grant_type='refresh_token',
            refresh_token=self._oidc_token["refresh_token"])

    def is_auth(self):
        return len(self._oidc_token) > 0

    @property
    def token(self):
        return self._oidc_token

    @token.setter
    def token(self, token):
        self._oidc_token = token

