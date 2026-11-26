from typing import Self


class MissingDatabaseVariableError(RuntimeError):
    MESSAGE = "{name} must be set when DATABASE_ENGINE=postgresql"

    @classmethod
    def for_name(cls, name: str) -> Self:
        return cls(cls.MESSAGE.format(name=name))


class UnsupportedDatabaseEngineError(RuntimeError):
    MESSAGE = "DATABASE_ENGINE must be either 'sqlite' or 'postgresql'"

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)
