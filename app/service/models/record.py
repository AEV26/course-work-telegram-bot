from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional

import pytz


@dataclass
class Record:
    date: datetime = field(default_factory=datetime.now)
    rent: float = field(default=float(0))
    heat: float = field(default=float(0))
    exploitation: float = field(default=float(0))
    mop: float = field(default=float(0))
    renovation: float = field(default=float(0))
    tbo: float = field(default=float(0))
    electricity: float = field(default=float(0))
    earth_rent: float = field(default=float(0))
    other: float = field(default=float(0))
    security: float = field(default=float(0))

    @staticmethod
    def from_dict(data: dict):
        date = data["date"]
        rent = data["rent"]
        heat = data["heat"]
        exploitation = data["exploitation"]
        mop = data["mop"]
        renovation = data["renovation"]
        tbo = data["tbo"]
        electricity = data["electricity"]
        earthrent = data["earth_rent"]
        other = data["other"]
        security = data["security"]

        return Record(
            date=datetime.fromisoformat(date),
            rent=rent,
            heat=heat,
            exploitation=exploitation,
            mop=mop,
            renovation=renovation,
            tbo=tbo,
            electricity=electricity,
            earth_rent=earthrent,
            other=other,
            security=security,
        )

    def to_dict(self) -> dict:
        data = asdict(self)
        data["date"] = self.date.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return data


@dataclass
class UpdateRecordInput:
    date: Optional[datetime] = field(default=None)
    rent: Optional[float] = field(default=None)
    heat: Optional[float] = field(default=None)
    exploitation: Optional[float] = field(default=None)
    mop: Optional[float] = field(default=None)
    renovation: Optional[float] = field(default=None)
    tbo: Optional[float] = field(default=None)
    electricity: Optional[float] = field(default=None)
    earth_rent: Optional[float] = field(default=None)
    other: Optional[float] = field(default=None)
    security: Optional[float] = field(default=None)

    def to_dict(self) -> dict:
        data = asdict(self)
        if self.date is not None:
            data["date"] = self.date.astimezone(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
        return data
