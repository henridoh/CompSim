class Register:
    def __init__(self, cap=0xff):
        self._value = 0

        self.cap = cap

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, x):
        self._value = x & self.cap

class Adder(Register):
    def __init__(self, a, b):
        super().__init__()
        self.a = a
        self.b = b

    @property
    def value(self):
        return self.a.value + self.b.value

class FlagRegister(Register):
    def __init__(self, cap=2):
        super().__init__(cap=cap)

    def __setitem__(self, key, value):
        self.value ^= (-value ^ self.value) & (1 << key)

    def __getitem__(self, item):
        return (self.value >> item) & 1
