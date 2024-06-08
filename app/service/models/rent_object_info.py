from dataclasses import dataclass
from .record import Record


@dataclass
class RecordInfo:
    record: Record
    income: float
    expenses: float
    profit: float
    income_by_area: float
    expenses_by_area: float
    profit_by_area: float

    @staticmethod
    def from_dict(data: dict) -> "RecordInfo":
        record = Record.from_dict(data)
        income = data.get("income")
        expenses = data.get("expenses")
        profit = data.get("profit")
        income_by_area = data.get("income_by_area")
        expenses_by_area = data.get("expenses_by_area")
        profit_by_area = data.get("profit_by_area")
        return RecordInfo(
            record=record,
            income=income,
            expenses=expenses,
            profit=profit,
            income_by_area=income_by_area,
            expenses_by_area=expenses_by_area,
            profit_by_area=profit_by_area,
        )


@dataclass
class RentObjectInfo:
    name: str
    description: str
    area: float
    records_info: list[RecordInfo]

    @staticmethod
    def from_dict(data: dict) -> "RentObjectInfo":
        name = data.get("name")
        description = data.get("description")
        area = data.get("area")

        records_info = []
        for el in data.get("records_info") or []:
            records_info.append(RecordInfo.from_dict(el))

        return RentObjectInfo(
            name=name, description=description, area=area, records_info=records_info
        )

    def get_average_income(self) -> float:
        return sum(record.income for record in self.records_info) / len(
            self.records_info
        )

    def get_average_income_with_tax(self) -> float:
        return self.get_average_income() * 0.94

    def get_average_expenses(self) -> float:
        return sum(record.expenses for record in self.records_info) / len(
            self.records_info
        )
