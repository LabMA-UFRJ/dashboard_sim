from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict

import pandas as pd


class DataLoader:
    """Carrega e normaliza arquivos CSV com dados de cobertura."""

    def __init__(self, *, base_path: Path | str | None = None, config: Dict | None = None) -> None:
        if base_path is not None:
            self.base_path = Path(base_path)
        elif config is not None:
            data_paths = config.get("data_paths", {})
            raw_path = data_paths.get("raw")
            if raw_path is None:
                raise ValueError("Chave 'data_paths.raw' ausente no config.")
            self.base_path = Path(raw_path)
        else:  # pragma: no cover - proteção de uso incorreto
            raise ValueError("Informe 'base_path' ou 'config' ao inicializar DataLoader.")

    def load_csv(self, csv_path: Path | str) -> pd.DataFrame:
        csv_path = Path(csv_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")

        header, first_row = self._peek(csv_path)
        if first_row is not None and len(first_row) == len(header) + 1:
            df = pd.read_csv(
                csv_path,
                header=None,
                names=header + ["_EXTRA"],
                skiprows=1,
                engine="c",
                encoding="utf-8-sig",
                quotechar='"',
            ).drop(columns=["_EXTRA"])
            return self._clean_cols(df)

        try:
            df = pd.read_csv(csv_path, sep=None, engine="python", encoding="utf-8-sig")
            return self._clean_cols(df)
        except pd.errors.ParserError:
            pass

        for sep in (";", ",", "\t", "|"):
            try:
                df = pd.read_csv(
                    csv_path,
                    sep=sep,
                    engine="python",
                    encoding="utf-8-sig",
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL,
                    index_col=False,
                )
                return self._clean_cols(df)
            except pd.errors.ParserError:
                continue

        df = pd.read_csv(
            csv_path,
            sep=None,
            engine="python",
            encoding="utf-8-sig",
            on_bad_lines="skip",
        )
        return self._clean_cols(df)

    def load_company_data(self, company: str, year: int, insurance_type: str) -> pd.DataFrame:
        """Fluxo legado para leituras por empresa/ano a partir de arquivos parquet."""
        path = self.base_path / str(year) / company / insurance_type
        if not path.exists():
            raise FileNotFoundError(f"Path {path} não encontrado")

        dataframes = [pd.read_parquet(file_path) for file_path in path.glob("*.parquet")]
        return pd.concat(dataframes, ignore_index=True) if dataframes else pd.DataFrame()

    @staticmethod
    def _peek(csv_path: Path) -> tuple[list[str], list[str] | None]:
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader)
            first = next(reader, None)
        return header, first

    @staticmethod
    def _clean_cols(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        if ("REF_INFO" not in df.columns) and (df.index.name == "REF_INFO"):
            df = df.reset_index()

        if "REF_INFO" not in df.columns and pd.api.types.is_integer_dtype(df.index):
            idx = df.index.to_series()
            if idx.between(1900, 2100, inclusive="both").all():
                df = df.reset_index().rename(columns={"index": "REF_INFO"})
            else:
                df = df.reset_index()

        df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
        df.columns = df.columns.astype(str).str.strip()

        if "ENTRADAS" in df.columns and "ENTRADA" not in df.columns:
            df = df.rename(columns={"ENTRADAS": "ENTRADA"})
        elif "ENTRADAS" in df.columns and "ENTRADA" in df.columns:
            df["ENTRADA"] = (
                pd.to_numeric(df["ENTRADA"], errors="coerce").fillna(0)
                + pd.to_numeric(df.pop("ENTRADAS"), errors="coerce").fillna(0)
            )

        if "EXPOSICAOO" in df.columns:
            df = df.rename(columns={"EXPOSICAOO": "EXPOSICAO"})

        if "REF_INFO" in df.columns:
            df["REF_INFO"] = pd.to_numeric(df["REF_INFO"], errors="coerce").astype("Int64")
            df = df.dropna(subset=["REF_INFO"])

        if "COD_EMP" in df.columns:
            ser = df["COD_EMP"].astype(str).str.strip()
            df["COD_EMP"] = ser.mask(ser.str.lower().isin({"nan", "none", ""}))

        if "EMP" in df.columns:
            df["EMP"] = df["EMP"].astype(str).str.strip()

        if "SEXO" in df.columns:
            df["SEXO"] = df["SEXO"].astype(str).str.strip().str.upper()

        return df


__all__ = ["DataLoader"]
