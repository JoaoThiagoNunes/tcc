from __future__ import annotations
import re
from typing import List


CNPJ_MASKED = re.compile(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b")
CNPJ_DIGITS = re.compile(r"\b\d{14}\b")
DATE_DD_MM_YYYY = re.compile(r"\b\d{2}/\d{2}/\d{4}\b")
MONEY_BR = re.compile(r"R\$\s*([\d]{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{2})?)", re.IGNORECASE)
DIGITS_LONG = re.compile(r"\d{44,48}")


def normalize_cnpj_digits(raw: str) -> str:
    return "".join(ch for ch in raw if ch.isdigit())

def find_cnpjs(text: str) -> List[str]:
    found: List[str] = []
    for m in CNPJ_MASKED.finditer(text):
        found.append(m.group(0))
    for m in CNPJ_DIGITS.finditer(text):
        digits = m.group(0)
        if len(digits) == 14:
            found.append(digits)
    return found

def find_dates(text: str) -> List[str]:
    return DATE_DD_MM_YYYY.findall(text)

def find_money_values(text: str) -> List[float]:
    values: List[float] = []
    for m in MONEY_BR.finditer(text):
        raw = m.group(1)
        normalized = raw.replace(".", "").replace(",", ".")
        try:
            values.append(float(normalized))
        except ValueError:
            continue
    return values

def find_codigo_barras_candidate(text: str) -> str | None:
    compact = re.sub(r"\s+", "", text)
    m = DIGITS_LONG.search(compact)
    return m.group(0) if m else None
