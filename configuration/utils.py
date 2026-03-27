from __future__ import annotations

from typing import Iterable

from .models import Currency, Language, StatusCatalog


def get_currency_choices(fallback_codes: Iterable[str] | None = None) -> list[tuple[str, str]]:
    rows = list(Currency.objects.filter(is_active=True).order_by("sort_order", "code").values_list("code", "name", "symbol"))
    if rows:
        return [(code, f"{code} · {name}" + (f" ({symbol})" if symbol else "")) for code, name, symbol in rows]
    fallback_codes = list(fallback_codes or ["EUR"])
    return [(code, code) for code in fallback_codes]


def get_language_choices(fallback_codes: Iterable[str] | None = None) -> list[tuple[str, str]]:
    rows = list(Language.objects.filter(is_active=True).order_by("sort_order", "code").values_list("code", "name"))
    if rows:
        return [(code, f"{code} · {name}") for code, name in rows]
    fallback_codes = list(fallback_codes or ["es"])
    return [(code, code) for code in fallback_codes]


def get_status_choices(status_group: str, default_choices: Iterable[tuple[str, str]]) -> list[tuple[str, str]]:
    default_map = {code: label for code, label in default_choices}
    configured = list(
        StatusCatalog.objects.filter(status_group=status_group, is_active=True)
        .order_by("sort_order", "label")
        .values_list("code", "label")
    )
    if not configured:
        return list(default_choices)

    choices: list[tuple[str, str]] = []
    configured_codes = []
    for code, label in configured:
        configured_codes.append(code)
        choices.append((code, label or default_map.get(code, code)))
    for code, label in default_choices:
        if code not in configured_codes:
            choices.append((code, label))
    return choices
