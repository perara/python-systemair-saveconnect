import random
import time
from json import dumps


class Login:

    def __init__(self, iam, password):

        self.iam_id = iam
        self.password = password
        self.client_id = "client-%s-%s" % (int(time.time() * 1000), random.randint(1, 9999))

    def __str__(self):
        return dumps(dict(
            type="LOGIN",
            machineId=self.iam_id,
            passCode=self.password,
            sessionClientId=self.client_id
        ))


class Read:

    def __init__(self, commands):
        self.commands = commands

    def __str__(self):
        return dumps(dict(
            type="READ",
            idsToRead=self.commands
        ))


class Write:

    def __init__(self, commands):
        self.commands = commands

    def __str__(self):
        return dumps(dict(
            type="WRITE",
            valuesToWrite=self.commands
        ))