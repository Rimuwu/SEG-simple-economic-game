from dataclasses import dataclass


@dataclass
class Prison:
    """Настройки тюрьмы"""
    on_reputation: int  # Репутация при которой сажают в тюрьму
    stages: int  # Количество ходов в тюрьме
    new_cell: bool  # При выходе из тюрьмы игрок попадает на новую клетку


@dataclass
class ContractReputation:
    """Настройки репутации за контракты"""
    completed: int  # Репутация за выполненный контракт
    failed: int  # Репутация за проваленный контракт


@dataclass
class TaxReputation:
    """Настройки репутации за налоги"""
    paid: int  # Репутация за уплаченный налог
    late: int  # Репутация за просроченный налог
    not_paid_stages: int  # Количество ходов с неоплаченным налогом после которого сажают в тюрьму


@dataclass
class CreditReputation:
    """Настройки репутации за кредиты"""
    gained: int  # Репутация за получение кредита
    lost: int  # Репутация за потерю кредита
    max_overdue: int  # Максимальное количество просроченных платежей по кредиту после которого сажают в тюрьму


@dataclass
class Reputation:
    """Система репутации в игре"""
    start: int  # Начальная репутация
    prison: Prison
    contract: ContractReputation
    tax: TaxReputation
    credit: CreditReputation

    @classmethod
    def load_from_json(cls, data: dict):
        prison = Prison(**data["prison"])
        contract = ContractReputation(**data["contract"])
        tax = TaxReputation(**data["tax"])
        credit = CreditReputation(**data["credit"])

        return cls(
            start=data["start"],
            prison=prison,
            contract=contract,
            tax=tax,
            credit=credit
        )