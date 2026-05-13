from __future__ import annotations

import pandas as pd
from pathlib import Path
from typing import Dict

from src.core.data_loader import DataLoader
from src.settings import (
    BASE_PATH,
    CONFIG,
    COUNT_VARIANTS,
    FILE_TEMPLATES,
    FOLDER_NAMES,
)
from src.utils.logger import setup_logger

logger = setup_logger()


def _format_number(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def load_data(count_variant_label: str) -> Dict[str, pd.DataFrame]:
    """Carrega um dataframe por cobertura conforme o tipo de contagem selecionado."""
    if count_variant_label not in COUNT_VARIANTS:
        raise KeyError(f"Tipo de contagem desconhecido: {count_variant_label}")

    kind = COUNT_VARIANTS[count_variant_label]
    loader = DataLoader(base_path=BASE_PATH)

    dfs: Dict[str, pd.DataFrame] = {}
    missing: list[Path] = []

    for coverage, folder in FOLDER_NAMES.items():
        filename = FILE_TEMPLATES[coverage].format(kind=kind)
        csv_path = BASE_PATH / folder / filename

        try:
            df = loader.load_csv(csv_path)
        except FileNotFoundError:
            missing.append(csv_path)
            logger.warning(
                "[%s] Arquivo não encontrado para '%s': %s",
                coverage,
                count_variant_label,
                csv_path,
            )
            continue

        dfs[coverage] = df
        logger.info(
            "[%s] %s linhas carregadas de %s",
            coverage,
            _format_number(len(df)),
            csv_path,
        )

    if not dfs:
        raise FileNotFoundError(
            f"Nenhuma cobertura encontrada para '{count_variant_label}'. "
            "Verifique os arquivos disponíveis."
        )

    if missing:
        logger.warning(
            "Coberturas ausentes para '%s': %s",
            count_variant_label,
            "; ".join(str(path) for path in missing),
        )

    return dfs


config = CONFIG


def main() -> None:
    dfs = load_data("Registros")
    total = sum(len(df) for df in dfs.values())
    logger.info("Total de linhas carregadas: %s", _format_number(total))
    print(f"OK: {total:,} linhas".replace(",", "."))


if __name__ == "__main__":
    main()
