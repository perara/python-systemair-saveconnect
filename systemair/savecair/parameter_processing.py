import time


__boolean_conversion = {
    "inactive": False,
    "active": True
}


def components_filter_time_left(x): return int(time.time()) + int(x)


def fan_log_request_reset(x): return int(time.time()) + int(x)


def global_boolean(x):
    if x in __boolean_conversion:
        return __boolean_conversion[x]
    return x
