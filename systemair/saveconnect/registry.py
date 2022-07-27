
class RegisterWrite:

    def __init__(self, register, value):
        self._r = register
        self._v = value

    def dict(self):
        return {
            "register": self._r,
            "value": self._v
        }
