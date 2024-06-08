from datetime import datetime
from pathlib import Path
import xlsxwriter
from app.service.models.rent_object_info import RecordInfo, RentObjectInfo
from app.settings.config import PATH_TO_ROOT
from string import ascii_uppercase

PATH_TO_TMP = PATH_TO_ROOT / "tmp"


MONTHS = {
    1: "Янв",
    2: "Фев",
    3: "Март",
    4: "Апр",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Авг",
    9: "Сен",
    10: "Окт",
    11: "Нояб",
    12: "Дек",
}


def format_date(date: datetime) -> str:
    return f"{MONTHS[date.month]}-{date.year}"


class RentObjectXLSXWriter:
    HEADER_FORMAT = {"bold": 1, "align": "center"}
    MONEY_FORMAT = {
        "num_format": r'_-* #,##0.00\ "₽"_-;\-* #,##0.00\ "₽"_-;_-* "-"??\ "₽"_-;_-@'
    }

    RECORD_HEADERS = [
        "Месяц",
        "Аренда постоянная",
        "Аренда, итого",
        "Аренда, кв.метр итого",
        "Теплло",
        "Содержание (эксплуатация)",
        "МОП (ээ, ХВС, канализация, ГВС, ПДК, тепло)",
        "Капремонт",
        "ТБО",
        "Электрика счетчик (и МОП до дек.21)",
        "Аренда земли",
        "Прочие расходы",
        "Охрана",
        "Итого расходы",
        "Стимость расходов, за кв.метр",
        "Итого Д-Р",
        "Итого аренда, кв.метр",
    ]

    OBJECT_HEADERS = [
        "Метраж",
        "Количество месяцев",
        "Аренда (доход), среднемесячная",
        "Минус налог, 6%",
        "Аренда минус налог и затраты",
        "Итого год, минус затраты",
        "Окупаемость 5 лет",
        "Окупаемость 7 лет",
        "Окупаемость 8 лет",
        "Окупаемость 10 лет",
    ]

    RECORDS_INFO_START = 0
    RECORDS_SUMMARY_OFFSET = 3

    OBJECT_INFO_OFFSET = 3

    def create(self, object_info: RentObjectInfo, filepath=None):
        self.rent_object_info = object_info
        self.records_info = object_info.records_info
        self.records_count = len(self.records_info)
        self.RECORDS_SUMMARY_START = (
            self.RECORDS_INFO_START
            + 1
            + self.records_count
            + self.RECORDS_SUMMARY_OFFSET
        )
        self.OBJECT_INFO_START = (
            self.RECORDS_SUMMARY_START + 1 + self.OBJECT_INFO_OFFSET
        )

        filepath = filepath or PATH_TO_TMP / f"{self.rent_object_info.name}.xlsx"

        self.workbook = xlsxwriter.Workbook(filepath)
        self.worksheet = self.workbook.add_worksheet()

        self.header_format = self.workbook.add_format(self.HEADER_FORMAT)
        self.header_format.set_text_wrap()

        self.money_format = self.workbook.add_format(self.MONEY_FORMAT)

        self.write_records_data(self.worksheet)
        self.write_object_info(self.worksheet)
        self.workbook.close()
        return filepath

    def write_records_data(self, worksheet):
        self.write_headers(worksheet)
        self.write_rows(worksheet, self.records_info)
        self.writer_last_sum_line(worksheet, len(self.records_info))

    def write_headers(self, worksheet: xlsxwriter.workbook.Worksheet):
        row = self.RECORDS_INFO_START
        for col, header in enumerate(self.RECORD_HEADERS, start=1):
            worksheet.set_column_pixels(row, col, 105)
            worksheet.write(row, col, header, self.header_format)

    def write_rows(self, worksheet, records):
        start = self.RECORDS_INFO_START + 1
        for row, record in enumerate(records, start=start):
            self.write_row(worksheet, row, record)

    def write_row(self, worksheet, row: int, record_info: RecordInfo):
        record = record_info.record
        worksheet.write(row, 0, row)
        worksheet.write(row, 1, format_date(record.date))
        worksheet.write(row, 2, record.rent, self.money_format)
        worksheet.write(row, 3, record_info.income, self.money_format)
        worksheet.write(row, 4, record_info.income_by_area, self.money_format)
        worksheet.write(row, 5, record.heat, self.money_format)
        worksheet.write(row, 6, record.exploitation, self.money_format)
        worksheet.write(row, 7, record.mop, self.money_format)
        worksheet.write(row, 8, record.renovation, self.money_format)
        worksheet.write(row, 9, record.tbo, self.money_format)
        worksheet.write(row, 10, record.electricity, self.money_format)
        worksheet.write(row, 11, record.earth_rent, self.money_format)
        worksheet.write(row, 12, record.other, self.money_format)
        worksheet.write(row, 13, record.security, self.money_format)
        worksheet.write(row, 14, record_info.expenses, self.money_format)
        worksheet.write(row, 15, record_info.expenses_by_area, self.money_format)
        worksheet.write(row, 16, record_info.profit, self.money_format)
        worksheet.write(row, 17, record_info.profit_by_area, self.money_format)

    def writer_last_sum_line(self, worksheet, record_count: int):
        for i, letter in enumerate(ascii_uppercase[2:18], start=2):
            worksheet.write(
                record_count + self.RECORDS_SUMMARY_OFFSET,
                i,
                f"=SUM({letter}{2}:{letter}{record_count+2})",
                self.money_format,
            )

    def write_object_info(self, worksheet):
        self.write_object_headers(worksheet)
        self.write_object_data(worksheet)
        self.write_payback(worksheet)

    def write_object_headers(self, worksheet):
        row = self.OBJECT_INFO_START
        for col, header in enumerate(self.OBJECT_HEADERS, start=1):
            worksheet.set_column_pixels(row, col, 105)
            worksheet.write(row, col, header, self.header_format)

    def write_object_data(self, worksheet):
        row = self.OBJECT_INFO_START + 1
        average_profit = (
            self.rent_object_info.get_average_income_with_tax()
            - self.rent_object_info.get_average_expenses()
        )
        worksheet.write(row, 1, self.rent_object_info.area)
        worksheet.write(row, 2, self.records_count)
        worksheet.write(
            row, 3, self.rent_object_info.get_average_income(), self.money_format
        )
        worksheet.write(
            row,
            4,
            self.rent_object_info.get_average_income_with_tax(),
            self.money_format,
        )
        worksheet.write(row, 5, average_profit, self.money_format)
        worksheet.write(row, 6, average_profit * 12, self.money_format)
        worksheet.write(row, 7, average_profit * 12 * 5, self.money_format)
        worksheet.write(row, 8, average_profit * 12 * 7, self.money_format)
        worksheet.write(row, 9, average_profit * 12 * 8, self.money_format)
        worksheet.write(row, 10, average_profit * 12 * 10, self.money_format)

    def write_payback(self, worksheet):
        row = self.OBJECT_INFO_START + 1 + 2
        average_profit = (
            self.rent_object_info.get_average_income_with_tax()
            - self.rent_object_info.get_average_expenses()
        )
        worksheet.write(row, 6, "Стоимость")
        worksheet.write(
            row,
            7,
            average_profit * 12 * 5 / self.rent_object_info.area,
            self.money_format,
        )
        worksheet.write(
            row,
            8,
            average_profit * 12 * 7 / self.rent_object_info.area,
            self.money_format,
        )
        worksheet.write(
            row,
            9,
            average_profit * 12 * 8 / self.rent_object_info.area,
            self.money_format,
        )
        worksheet.write(
            row,
            10,
            average_profit * 12 * 10 / self.rent_object_info.area,
            self.money_format,
        )
