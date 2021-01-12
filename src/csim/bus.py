class Bus:
    def __init__(self, cap=255):
        self._value = 0
        self.cap = 255

    def _get_x(self):
        return self._value

    def _set_x(self, value: int):
        self._value = value & self.cap

    value = property(_get_x, _set_x)
