from dataclasses import dataclass, field
from typing import Optional
from .record import Record


@dataclass
class RentObject:
    name: str = field(default="")
    description: str = field(default="")
    area: float = field(default=0)
    records: list[Record] = field(default_factory=list)

    @staticmethod
    def from_dict(data: dict):
        name = data["name"]
        description = data["description"]
        area = data["area"]
        records = []
        for el in data["records"]:
            records.append(Record.from_dict(el))

        return RentObject(
            name=name, description=description, area=area, records=records
        )

    def to_dict(self) -> dict:
        records_dict = [r.to_dict() for r in self.records]
        return {
            "name": self.name,
            "description": self.description,
            "area": self.area,
            "records": records_dict,
        }


@dataclass
class UpdateRentObjectInput:
    name: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    area: Optional[float] = field(default=None)
