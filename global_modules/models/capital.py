from dataclasses import dataclass, field

@dataclass
class ReputationRange:
    min: int
    max: int

@dataclass
class CreditCondition:
    on_reputation: ReputationRange
    possible: bool
    without_interest: int = 0
    percent: float = 0.0

@dataclass
class ContributionCondition:
    on_reputation: ReputationRange
    possible: bool
    percent: float = 0.0

@dataclass
class Credit:
    min: int
    max: int
    conditions: list[CreditCondition] = field(default_factory=list)

@dataclass
class Contribution:
    min: int
    max: int
    conditions: list[ContributionCondition] = field(default_factory=list)

@dataclass
class Tax:
    auto_pay: bool
    small_business: float
    big_business: float
    big_on: int

@dataclass
class Bank:
    credit: Credit
    contribution: Contribution
    tax: Tax

@dataclass
class Capital:
    start: int
    bank: Bank

    @classmethod
    def load_from_json(cls, data: dict) -> 'Capital':
        bank_data = data['bank']

        credit_conditions = [
            CreditCondition(
                on_reputation=ReputationRange(**cond['on_reputation']),
                possible=cond['possible'],
                without_interest=cond.get('without_interest', 0),
                percent=cond.get('percent', 0.0)
            )
            for cond in bank_data['credit']['conditions']
        ]
        
        contribution_conditions = [
            ContributionCondition(
                on_reputation=ReputationRange(**cond['on_reputation']),
                possible=cond['possible'],
                percent=cond['percent']
            )
            for cond in bank_data['contribution']['conditions']
        ]
        
        credit = Credit(
            min=bank_data['credit']['min'],
            max=bank_data['credit']['max'],
            conditions=credit_conditions
        )
        
        contribution = Contribution(
            min=bank_data['contribution']['min'],
            max=bank_data['contribution']['max'],
            conditions=contribution_conditions
        )

        tax = Tax(**bank_data['tax'])

        bank = Bank(credit=credit, contribution=contribution, tax=tax)
        
        return cls(start=data['start'], bank=bank)