from enum import StrEnum, auto


class TransactionType(StrEnum):
    income = auto()
    expense = auto()
