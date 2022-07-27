

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


class Airflow:
    OFF = "off"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class UserModes:
    AUTO = "auto"
    MANUAL = "manual"
    CROWDED = "crowded"
    REFRESH = "refresh"
    FIREPLACE = "fireplace"
    AWAY = "away"
    HOLIDAY = "holiday"
