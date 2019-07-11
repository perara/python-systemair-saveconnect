"""SystemAIR API commands."""
import random
import time
from json import dumps


def login(iam_id, password):
    """
    Login command sequence to SystemAIR Savecair.
    :param iam_id: The iam_id provided at installation
    :param password: The password set in the savecair app
    :return:
    """

    client_id = "client-%s-%s" % (int(time.time() * 1000), random.randint(1, 9999))

    return dumps(
        {'type': "LOGIN", 'machineId': iam_id, 'passCode': password, 'sessionClientId': client_id}
    )


def read(items):
    """
    Request read of items for the ventilation unit.
    :param items: List
    :return:
    """
    return dumps(dict(
        type="READ",
        idsToRead=items
    ))


def write(**kwargs):
    """
    Write a dictionary of kp to the SaveCair API.
    :param kwargs: dict
    :return:
    """
    return dumps(dict(
        type="WRITE",
        valuesToWrite=kwargs
    ))
