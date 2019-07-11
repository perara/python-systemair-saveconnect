from datetime import datetime, timedelta


RECV_TYPE_ERROR = "ERROR"
RECV_TYPE_LOGGED_IN = "LOGGED_IN"
RECV_TYPE_READ = "READ"
RECV_TYPE_VALUE_CHANGED = "VALUE_CHANGED"


SA_FAN_MODE_OFF = "off"
SA_FAN_MODE_LOW = "low"
SA_FAN_MODE_MEDIUM = "medium"
SA_FAN_MODE_HIGH = "high"
SA_FAN_MODE_MAXIMUM = "maximum"

FAN_MODE = {
    1: SA_FAN_MODE_OFF,
    2: SA_FAN_MODE_LOW,
    3: SA_FAN_MODE_MEDIUM,
    4: SA_FAN_MODE_HIGH,
    5: SA_FAN_MODE_MAXIMUM
}

ALARM_MODES = {
    "active": True,
    "inactive": False
}

SA_OPERATION_MODE_AUTO = "auto"
SA_OPERATION_MODE_MANUAL = "manual"
SA_OPERATION_MODE_CROWDED = "crowded"
SA_OPERATION_MODE_REFRESH = "refresh"
SA_OPERATION_MODE_FIREPLACE = "fireplace"
SA_OPERATION_MODE_HOLIDAY = "holiday"
SA_OPERATION_MODE_IDLE = "idle"

# Custom
SA_OPERATION_MODE_OFF = "off"

USER_MODE = {
    0: SA_OPERATION_MODE_AUTO,
    1: SA_OPERATION_MODE_MANUAL,
    2: SA_OPERATION_MODE_CROWDED,
    3: SA_OPERATION_MODE_REFRESH,
    4: SA_OPERATION_MODE_FIREPLACE,
    5: SA_OPERATION_MODE_IDLE,
    6: SA_OPERATION_MODE_HOLIDAY
}

POSTPROCESS_NO = lambda x: x
POSTPROCESS_TEMPERATURE = lambda x: x / 10.0
POSTPROCESS_DAYS_UNTIL = lambda x: ((datetime.now() + timedelta(seconds=x)) - datetime.today()).days
POSTPROCESS_OPERATION = lambda x: USER_MODE[int(x)]
POSTPROCESS_FAN_MODE = lambda x: FAN_MODE[int(x)]
POSTPROCESS_ALARM = lambda x: ALARM_MODES[str(x)]

# Custom
SENSOR_CUSTOM_OPERATION = "custom_operation"
SENSOR_CUSTOM_FAN_MODE = 'custom_fan_mode'

# TODO -- Other useless
"""
main_iaq  # Main (Primary)  indoor air quality - Example: economic
control_regulation_airflow_manual_fan_stop  # Enables Manual STOP in fan options - Example: True
control_regulation_demand_rh_status  # Demand humidity status: True False
control_regulation_demand_co2_status  # Demand co2 status: TRue False
control_regulation_temp_unit
control_regulation_airflow_type
control_regulation_airflow_unit_man_perc

week_schedule_any_defined
main_temperature_offset
eco_mode  # Dunno why i would need this
filter_lock
week_schedule_lock
fan_log_request_reset
"""

SENSOR_FAN_SPEED_EXTRACT = 'digital_input_tacho_saf_value'
SENSOR_FAN_SPEED_SUPPLY = 'digital_input_tacho_eaf_value'

SENSOR_TEMPERATURE_OUTDOOR = 'outdoor_air_temp'
SENSOR_TEMPERATURE_SUPPLY = 'supply_air_temp'
SENSOR_TEMPERATURE_EXTRACT = 'pdm_input_temp_value'

SENSOR_CURRENT_HUMIDITY = 'pdm_input_rh_value'  # rh_sensor


SENSOR_FILTER_TIME = 'components_filter_time_left'

# Airflow
SENSOR_CURRENT_FAN_MODE = "main_airflow"  # Current airflow - High, Normal, Low, Off

# Operation
SENSOR_CURRENT_OPERATION = "main_user_mode"

# User LOck
SENSOR_USER_LOCK = "user_lock"

# User mode hardcoded airflow for supply and extract
SENSOR_CROWDED_SUPPLY = 'user_mode_crowded_supply'
SENSOR_REFRESH_SUPPLY = 'user_mode_refresh_supply'
SENSOR_AWAY_SUPPLY = 'user_mode_away_supply'
SENSOR_HOLIDAY_SUPPLY = 'user_mode_holiday_supply'
SENSOR_FIREPLACE_SUPPLY = 'user_mode_fireplace_supply'
SENSOR_AUTO_SUPPLY = 'user_mode_auto_supply'
SENSOR_CROWDED_EXTRACT = 'user_mode_crowded_extract'
SENSOR_REFRESH_EXTRACT = 'user_mode_refresh_extract'
SENSOR_AWAY_EXTRACT = 'user_mode_away_extract'
SENSOR_HOLIDAY_EXTRACT = 'user_mode_holiday_extract'
SENSOR_FIREPLACE_EXTRACT = 'user_mode_fireplace_extract'
SENSOR_AUTO_EXTRACT = 'user_mode_auto_extract'

# Activated Functions
SENSOR_FUNCTION_COOLING = 'function_active_cooling'
SENSOR_FUNCTION_VACUUM_CLEANER = 'function_active_vacuum_cleaner'
SENSOR_FUNCTION_FREE_COOLING = 'function_active_free_cooling'
SENSOR_FUNCTION_HEATING = 'function_active_heating'
SENSOR_FUNCTION_DEFROSTING = 'function_active_defrosting'
SENSOR_FUNCTION_HEAT_RECOVERY = 'function_active_heat_recovery'
SENSOR_FUNCTION_COOLING_RECOVERY = 'function_active_cooling_recovery'
SENSOR_FUNCTION_MOISTURE_TRANSFER = 'function_active_moisture_transfer'
SENSOR_FUNCTION_SECONDARY_AIR = 'function_active_secondary_air'
SENSOR_FUNCTION_COOKER_HOOD = 'function_active_cooker_hood'
SENSOR_FUNCTION_HEATER_COOLDOWN = 'function_active_heater_cooldown'
SENSOR_FUNCTION_SERVICE_USER_LOCK = 'function_active_service_user_lock'


# Alarms
SENSOR_ALARM_FROST_PROTECTION = 'alarm_frost_prot_state'  # Frost protection
SENSOR_ALARM_FROST_PROTECTION_SENSOR = 'alarm_fpt_state'  # Frost protection sensor (FPT)
SENSOR_ALARM_DEFROST = 'alarm_defrosting_state'  # Defrosting malfunction
SENSOR_ALARM_SUPPLY_RPM = 'alarm_saf_rpm_state'  # Supply air fan RPM  error
SENSOR_ALARM_EXTRACT_RPM = 'alarm_eaf_rpm_state'  # Extract air fan RPM error
SENSOR_ALARM_SUPPLY_FLOW_PRESSURE = 'alarm_saf_ctrl_state'  # Flow or presure alarm on Supply
SENSOR_ALARM_EXTRACT_FLOW_PRESSURE = 'alarm_eaf_ctrl_state'  # Flor or pressure on Extract
SENSOR_ALARM_ELECTRICAL_HEATER = 'alarm_emt_state'  # Emergency thermostat (Error on electrical heater)
SENSOR_ALARM_BYPASS_DAMPER = 'alarm_bys_state'  # Malfunction bypass damper
SENSOR_ALARM_ROTARY_EXCHANGER = 'alarm_rgs_state'  # Rotatiion alarm for rotary exchanger
SENSOR_ALARM_BYPASS_DAMPER_2 = 'alarm_secondary_air_state'  # Wrong position of damper in extract exhaust stream of exchanger
SENSOR_ALARM_OUTDOOR_TEMP_SENSOR = 'alarm_oat_state'  # Error on temp sensor outdoor air
SENSOR_ALARM_REHEATER_TEMP_SENSOR = 'alarm_oht_state'  # Error on temp sensor on reheater
SENSOR_ALARM_SUPPLY_TEMP_SENSOR = 'alarm_sat_state'  # Error on temperature sensor for supply air
SENSOR_ALARM_INDOOR_TEMP_SENSOR = 'alarm_rat_state'  # Error on room air sensor
SENSOR_ALARM_EXTRACT_TEMP_SENSOR = 'alarm_eat_state'  # Error on exctract air sensor
SENSOR_ALARM_PREHEATER_TEMP_SENSOR = 'alarm_ect_state'  # ERROR ON PRE-HEATER EMERGENCY thermostat
SENSOR_ALARM_EFFICIENCY_TEMP_SENSOR = 'alarm_eft_state'  # Error on efficency temperature sensor
SENSOR_ALARM_PDM_RH = 'alarm_pdm_rhs_state'  # Error on PDM sensor for rh
SENSOR_ALARM_PDM_TEMP = 'alarm_pdm_eat_state'  # Error on PDM Sensor for temperature
SENSOR_ALARM_CHANGE_FILTER = 'alarm_filter_state'  # Change the filter ERROR
SENSOR_ALARM_EXTRA_CONTROLLER = 'alarm_extra_controller_state'  #
SENSOR_ALARM_EXTERNAL_STOP = 'alarm_external_stop_state'  # uNIT IS STOPPED BY EXTERNAL signal
SENSOR_ALARM_MANUAL_STOP = 'alarm_manual_fan_stop_state'  # Manaual Stop selected OFF
SENSOR_ALARM_REHEATER_OVERHEAT = 'alarm_overheat_temperature_state'  # Temperature of reheater is to high
SENSOR_ALARM_SUPPLY_TEMP_LOW = 'alarm_low_sat_state'  # temperature on supply air is low
SENSOR_ALARM_CO2 = 'alarm_co2_state'  # CO2 alarm for indoor air quality
SENSOR_ALARM_RH = 'alarm_rh_state'  # humidity alarm for indoor aur quality
SENSOR_ALARM_INCORRECT_MANUAL_MODE = 'alarm_manual_mode_state'  # ONE OR MORE OF OUTPUTS ARE IN MANUAL SELECTED Mode


SENSOR_USER_MODE_CROWDED_SUPPLY = "user_lock"

# Read / Write
SENSOR_TARGET_TEMPERATURE = "main_temperature_offset"
SENSOR_MODE_CHANGE_REQUEST = 'mode_change_request'

# Postprocessing
POSTPROCESS_MAP = {
    SENSOR_CURRENT_FAN_MODE: POSTPROCESS_FAN_MODE,
    SENSOR_TEMPERATURE_OUTDOOR: POSTPROCESS_TEMPERATURE,
    SENSOR_TEMPERATURE_SUPPLY: POSTPROCESS_TEMPERATURE,
    SENSOR_TEMPERATURE_EXTRACT: POSTPROCESS_TEMPERATURE,
    SENSOR_FILTER_TIME: POSTPROCESS_DAYS_UNTIL,
    SENSOR_CURRENT_OPERATION: POSTPROCESS_OPERATION,
    SENSOR_TARGET_TEMPERATURE: POSTPROCESS_TEMPERATURE,




    SENSOR_ALARM_FROST_PROTECTION: POSTPROCESS_ALARM,
    SENSOR_ALARM_FROST_PROTECTION_SENSOR: POSTPROCESS_ALARM,
    SENSOR_ALARM_DEFROST: POSTPROCESS_ALARM,
    SENSOR_ALARM_SUPPLY_RPM: POSTPROCESS_ALARM,
    SENSOR_ALARM_EXTRACT_RPM: POSTPROCESS_ALARM,
    SENSOR_ALARM_SUPPLY_FLOW_PRESSURE: POSTPROCESS_ALARM,
    SENSOR_ALARM_EXTRACT_FLOW_PRESSURE: POSTPROCESS_ALARM,
    SENSOR_ALARM_ELECTRICAL_HEATER: POSTPROCESS_ALARM,
    SENSOR_ALARM_BYPASS_DAMPER: POSTPROCESS_ALARM,
    SENSOR_ALARM_ROTARY_EXCHANGER: POSTPROCESS_ALARM,
    SENSOR_ALARM_BYPASS_DAMPER_2: POSTPROCESS_ALARM,
    SENSOR_ALARM_OUTDOOR_TEMP_SENSOR: POSTPROCESS_ALARM,
    SENSOR_ALARM_REHEATER_TEMP_SENSOR: POSTPROCESS_ALARM,
    SENSOR_ALARM_SUPPLY_TEMP_SENSOR: POSTPROCESS_ALARM,
    SENSOR_ALARM_INDOOR_TEMP_SENSOR: POSTPROCESS_ALARM,
    SENSOR_ALARM_EXTRACT_TEMP_SENSOR: POSTPROCESS_ALARM,
    SENSOR_ALARM_PREHEATER_TEMP_SENSOR: POSTPROCESS_ALARM,
    SENSOR_ALARM_EFFICIENCY_TEMP_SENSOR: POSTPROCESS_ALARM,
    SENSOR_ALARM_PDM_RH: POSTPROCESS_ALARM,
    SENSOR_ALARM_PDM_TEMP: POSTPROCESS_ALARM,
    SENSOR_ALARM_CHANGE_FILTER: POSTPROCESS_ALARM,
    SENSOR_ALARM_EXTRA_CONTROLLER: POSTPROCESS_ALARM,
    SENSOR_ALARM_EXTERNAL_STOP: POSTPROCESS_ALARM,
    SENSOR_ALARM_MANUAL_STOP: POSTPROCESS_ALARM,
    SENSOR_ALARM_REHEATER_OVERHEAT: POSTPROCESS_ALARM,
    SENSOR_ALARM_SUPPLY_TEMP_LOW: POSTPROCESS_ALARM,
    SENSOR_ALARM_CO2: POSTPROCESS_ALARM,
    SENSOR_ALARM_RH: POSTPROCESS_ALARM,
    SENSOR_ALARM_INCORRECT_MANUAL_MODE: POSTPROCESS_ALARM


}

