"""
class Register:
    USER_MODE_READ = 1164
    USER_MODE_WRITE = 1161
    USER_MODE_HOLIDAY_TIME = 1100
    USER_MODE_AWAY_TIME = 1101
    USER_MODE_FIREPLACE_TIME = 1102
    USER_MODE_REFRESH_TIME = 1103
    USER_MODE_CROWDED_TIME = 1104

    AIRFLOW_WRITE = 1130
    TEMPERATURE_ECO_MODE_WRITE = 2504
    TEMPERATURE_OFFSET = 2000
"""


class Airflow:
    OFF = "off"
    MINIMUM = "minimum"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    MAXIMUM = "maximum"

class UserModes:
    AUTO = "auto"
    MANUAL = "manual"
    CROWDED = "crowded"
    REFRESH = "refresh"
    FIREPLACE = "fireplace"
    AWAY = "away"
    HOLIDAY = "holiday"


class APIRoutes:
    VIEWS_UNIT_INFORMATION_COMPONENTS_DESC = "/device/unit_information/components"
    VIEWS_UNIT_INFORMATION_SENSORS_DESC = "/device/unit_information/sensors"
    VIEWS_UNIT_INFORMATION_UNIT_INPUT_STATUS_DESC = "/device/unit_information/input_status"
    VIEWS_UNIT_INFORMATION_UNIT_OUTPUT_STATUS_DESC = "/device/unit_information/output_status"
    VIEWS_UNIT_INFORMATION_UNIT_DATE_TIME_TITLE = "/device/unit_information/date_time"
    VIEWS_UNIT_INFORMATION_UNIT_VERSION_DESC = "/device/unit_information/unit_version"
    ACTIVE_ALARMS = "/device/alarms/active_alarms"

