class Memory:
    def __init__(self, size=256, word_cap=255):
        self.data = [0 for _ in range(size)]
        self.word_cap = word_cap

    def __getitem__(self, key: int) -> int:
        assert type(key) == int
        try:
            return self.data[key]
        except IndexError:
            return 0

    def __setitem__(self, key: int, value: int):
        assert type(key) == int
        assert type(value) == int
        self.data[key] = value & self.word_cap
