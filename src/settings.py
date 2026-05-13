from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List

# Diretório de configuração (config/settings.json) ou variável de ambiente INSURANCE_DATA_BASE_PATH
_CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"
_SETTINGS_FILE = _CONFIG_DIR / "settings.json"

DEFAULT_BASE_PATH = Path(r"\\Projetos2\Wrk\Wrk_Maia\TRIPLICE\NEW\2025-2")

FOLDER_NAMES: Dict[str, str] = {
    "INV": "INV",
    "MOR": "MOR",
    "SOB": "SOB",
}

FILE_TEMPLATES: Dict[str, str] = {
    "INV": "ANALISES_INV_{kind}",
    "MOR": "ANALISES_MOR_{kind}",
    "SOB": "ANALISES_SOB_{kind}",
}

COUNT_VARIANTS: Dict[str, str] = {
    "Registros": "REG",
    "CPF Único": "CPF_UNI",
    "Indivíduos": "IND",
}

COMPANY_MAP: Dict[str, List[str] | str] = {
    "ASP": "11134",
    "BBR": "4707",
    "BRA": ["4740", "5444", "6106", "6866"],
    "CAP": "",
    "CEF": "8141",
    "CNP": "8141",
    "COM": "1937",
    "GBX": "10448",
    "GEN": "",
    "ICA": "",
    "ITA": "",
    "MAP": "",
    "MET": "",
    "MON": "",
    "PSG": "",
    "PVM": "",
    "SAN": "",
    "SNF": "",
    "SUL": "",
    "UMD": "",
    "ZUR": "",
}


def _load_base_path_from_file() -> Path | None:
    if not _SETTINGS_FILE.exists():
        return None

    try:
        text = _SETTINGS_FILE.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError:
        text = _SETTINGS_FILE.read_text(encoding="utf-8-sig").strip()

    text = text.lstrip("\ufeff")

    if not text:
        return None

    if text.startswith("{"):
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:  # pragma: no cover - erro raro
            raise ValueError(f"Arquivo de configuração inválido: {_SETTINGS_FILE}") from exc
        base_path = data.get("base_path")
    else:
        base_path = text

    if not base_path:
        return None
    return Path(base_path)


def resolve_base_path() -> Path:
    """Determina o caminho base dos dados com prioridade: variável > arquivo > padrão."""
    env_value = os.getenv("INSURANCE_DATA_BASE_PATH")
    if env_value:
        return Path(env_value).expanduser()

    file_value = _load_base_path_from_file()
    if file_value:
        return file_value

    return DEFAULT_BASE_PATH


BASE_PATH = resolve_base_path()

CONFIG = {
    "companies": sorted(COMPANY_MAP.keys()),
    "insurance_types": list(FOLDER_NAMES.keys()),
    "count_variants": list(COUNT_VARIANTS.keys()),
}


__all__ = [
    "BASE_PATH",
    "COMPANY_MAP",
    "CONFIG",
    "COUNT_VARIANTS",
    "DEFAULT_BASE_PATH",
    "FOLDER_NAMES",
    "FILE_TEMPLATES",
    "resolve_base_path",
]
