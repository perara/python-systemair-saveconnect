import json
import logging
import typing

from aiohttp import ClientError
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.exceptions import TransportAlreadyConnected

from systemair.saveconnect.data import SaveConnectData
from systemair.saveconnect.models import SaveConnectDevice
from systemair.saveconnect.registry import RegisterWrite
from .const import APIRoutes

_LOGGER = logging.getLogger(__name__)


class SaveConnectGraphQL:

    def __init__(self, data: SaveConnectData):
        self.data: SaveConnectData = data
        transport = AIOHTTPTransport(url="https://homesolutions.systemair.com/gateway/api")
        self.client = Client(
            transport=transport,
            fetch_schema_from_transport=True,
            execute_timeout=120
        )

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

        return self.data.update(device_id, response)

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

        try:
            response = await self.client.execute_async(
                query,
                variable_values=data
            )
        except TransportAlreadyConnected as e:
            raise ClientError(e)

        return self.data.update(device_id, response)

    async def queryGetDeviceData(self, device_id, change_mode=False):
        success = await self.queryDeviceView(
            device_id=device_id,
            route=f"/device/home{'' if not change_mode else '/changeMode'}"
        )
        return success

    async def queryGetAccount(self) -> typing.List['SaveConnectDevice']:
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
        response = await self.client.execute_async(query)

        for device_data in response["GetAccount"]["devices"]:
            self.data.update_device(device_data=device_data)

        return list(self.data.devices.values())

    async def queryDeviceInfo(self, device: SaveConnectDevice):
        statuses = []
        for route in [
            APIRoutes.VIEWS_UNIT_INFORMATION_COMPONENTS_DESC,
            APIRoutes.VIEWS_UNIT_INFORMATION_SENSORS_DESC,
            APIRoutes.VIEWS_UNIT_INFORMATION_UNIT_INPUT_STATUS_DESC,
            APIRoutes.VIEWS_UNIT_INFORMATION_UNIT_OUTPUT_STATUS_DESC,
            APIRoutes.VIEWS_UNIT_INFORMATION_UNIT_DATE_TIME_TITLE,
            APIRoutes.VIEWS_UNIT_INFORMATION_UNIT_VERSION_DESC,
        ]:
            status = await self.queryDeviceView(device.identifier, route)


            if not status:
                _LOGGER.error(f"queryDeviceInfo failed for route={route}")
            statuses.append(status)

        return all(statuses)
