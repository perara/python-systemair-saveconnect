import sys
from typing import Dict

from pydantic import BaseModel, typing, Field


class SaveConnectDeviceUnits(BaseModel):
    temperature: str
    pressure: str
    flow: str


class SaveConnectRegisterOption(BaseModel):
    value: str
    title: str
    logic: str


class SaveConnectRegisterItem(BaseModel):
    register_: int = Field(alias="register")
    defaultValue: typing.Union[str, int]
    options: typing.Optional[typing.Dict[str, SaveConnectRegisterOption]] = None
    readOnly: bool = None
    type: int
    value: typing.Union[str, int]
    internalDeviceType: int = None

    min: int = None
    max: int = None
    decimals: int = None
    increment: int = None
    exportable: bool = None
    conditionalProperties: typing.List[typing.Dict] = None


from .register import SaveConnectRegistry

# hacking this together.
sys.modules[SaveConnectRegistry.__module__].SaveConnectRegisterItem = SaveConnectRegisterItem
SaveConnectRegistry.update_forward_refs()


class SaveConnectDevice(BaseModel):
    name: str
    identifier: str
    connectionStatus: str
    startupWizardRequired: str = None
    updateInProgress: str = None
    street: str = None
    zipcode: int = None
    city: str = None
    country: str = None
    serviceLocked: bool = None
    filterLocked: bool = None
    weekScheduleLocked: bool = None
    hasAlarms: bool = None
    units: SaveConnectDeviceUnits
    registry: 'SaveConnectRegistry' = None

    cb = []

    async def update(self, api):
        return await api.read_data(self)

    def add_update_callback(self, cb):
        self.cb.append(cb)


def update(self, data: Dict):
    for k, v in data.items():  # self.validate(data).dict().items():
        # log.debug(f"updating value of '{k}' from '{getattr(self, k, None)}' to '{v}'")
        setattr(self, k, v)
    return self
