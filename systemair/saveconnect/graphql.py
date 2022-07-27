import json

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

from systemair.saveconnect.data import SaveConnectData
from systemair.saveconnect.registry import RegisterWrite


class SaveConnectGraphQL:

    def __init__(self, data: SaveConnectData):
        self.data: SaveConnectData = data
        transport = AIOHTTPTransport(url="https://homesolutions.systemair.com/gateway/api")
        self.client = Client(transport=transport, fetch_schema_from_transport=True)

    def set_access_token(self, _oidc_token):
        self.client.transport.headers = {
            "x-access-token": _oidc_token["access_token"]
        }

    async def queryWriteDeviceValues(self, device_id, register_pair: RegisterWrite, is_import=False):
        query = gql(
            """
                mutation ($input: WriteDeviceValuesInputType!) {
                  WriteDeviceValues(input: $input)
                }
            """
        )

        data = dict(
            input={
                "deviceId": device_id,
                "import": is_import,
                "registerValues": json.dumps([
                    register_pair.dict()
                ])
            }
        )

        response = await self.client.execute_async(
            query,
            variable_values=data
        )

        self.data.update(device_id, response)
        return response

    async def queryDeviceView(self, device_id, route):
        query = gql(
            """
            mutation ($input: GetDeviceViewInput!) {
              GetDeviceView(input: $input) {
                route
                elements
                dataItems
                title
                translationVariables
              }
            }
            """,
        )

        data = dict(
            input=dict(
                deviceId=device_id,
                route=route
            )
        )

        response = await self.client.execute_async(
            query,
            variable_values=data
        )

        self.data.update(device_id, response)

        return response

    async def queryGetDeviceData(self, device_id, change_mode=False):
        response = await self.queryDeviceView(
            device_id=device_id,
            route=f"/device/home{'' if not change_mode else '/changeMode'}"
        )

        self.data.update(device_id, response)

        return response

    async def queryGetAccount(self):
        query = gql("""
            {
              GetAccount {
                email
                firstName
                lastName
                city
                country
                locale
                phoneNumber
                street
                role
                zipCode
                permissions
                exists
                disabled
                devices {
                  name
                  identifier
                  connectionStatus
                  startupWizardRequired
                  updateInProgress
                  units {
                    temperature
                    pressure
                    flow
                  }
                  street
                  zipcode
                  city
                  country
                  serviceLocked
                  filterLocked
                  weekScheduleLocked
                  hasAlarms
                }
                notifications {
                  id
                  title
                  description
                  type
                  unread
                  email
                  properties
                  createdAt
                }
                company {
                  companyName
                  referenceEmail
                  referenceName
                  responsiblePerson
                  responsiblePersonPhoneNumber
                }
              }
            }
        """)
        return await self.client.execute_async(query)
