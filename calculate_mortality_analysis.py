"""
Mortality Analysis and mx Calculation Pipeline
===============================================

This module provides a complete pipeline for:
1. Loading death records and population data
2. Standardizing data formats
3. Calculating mortality rates (mx) by age and demographic categories
4. Generating summary statistics
5. Exporting results to CSV for visualization

Author: Maia
Date: 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== DATA PATHS ====================

MICRODADOS_DIR = Path("//Projetos2/Wrk/SIM-DATASUS/MICRODADOS/")
ELEITORADO_DIR = Path("//Projetos2/Wrk/SIM-DATASUS/ELEITORADO/")
OUTPUT_DIR = Path("./data/processed")



# ==================== DATA DICTIONARIES ====================

DICTIONARY_LABELS = {
    'estado_civil': {
        '1': 'Solteiro(a)', 
        '2': 'Casado(a)', 
        '3': 'Viúvo(a)', 
        '4': 'Divorciado(a)', 
        '5': 'União Consensual'
    },
    'sexo': {
        '1': 'Masculino', 
        '2': 'Feminino'
    },
    'escolaridade': {
        '1': 'Nenhuma', 
        '2': '1 a 3 anos', 
        '3': '4 a 7 anos', 
        '4': '8 a 11 anos', 
        '5': '12 anos ou mais'
    },
    'raca_cor': {
        '1': 'Branca', 
        '2': 'Preta', 
        '3': 'Amarela', 
        '4': 'Parda', 
        '5': 'Indígena'
    }
}


# ==================== UTILITY FUNCTIONS ====================

def standardize_data(df, age_col=None, count_col=None, category_col=None):
    """
    Standardize any demographic data to a common format.
    
    Parameters:
    - df: Input DataFrame
    - age_col: Name of the age/idade column (if None, auto-detect)
    - count_col: Name of the count/total column (if None, auto-detect)
    - category_col: Optional category column name (e.g., 'raca_cor', 'sexo')
    
    Returns:
    - Standardized DataFrame with columns: ['idade', 'count'] or ['idade', 'count', category_col]
    """
    df_std = df.copy()
    
    # AUTO-DETECT AGE COLUMN
    if age_col is None:
        age_candidates = [col for col in df_std.columns 
                         if col.lower() in ['idade', 'age', 'age_group', 'faixa etária']]
        if not age_candidates:
            raise ValueError(f"Could not find age column. Available columns: {df_std.columns.tolist()}")
        age_col = age_candidates[0]
    
    # AUTO-DETECT COUNT COLUMN (if not the age column)
    if count_col is None:
        exclude_cols = {age_col, category_col} if category_col else {age_col}
        numeric_cols = df_std.select_dtypes(include=['int64', 'float64']).columns.tolist()
        count_candidates = [col for col in numeric_cols if col not in exclude_cols]
        
        if not count_candidates:
            raise ValueError(f"Could not find count column. Available numeric columns: {numeric_cols}")
        
        count_col = count_candidates[0]
    
    # Standardize column names
    rename_map = {age_col: 'idade', count_col: 'count'}
    if category_col and category_col in df_std.columns:
        rename_map[category_col] = 'category'
    
    df_std.rename(columns=rename_map, inplace=True)
    
    # Convert idade to integer
    df_std['idade'] = df_std['idade'].astype(float).astype(int)
    
    # Ensure count is numeric
    df_std['count'] = pd.to_numeric(df_std['count'], errors='coerce')
    
    # Select only necessary columns
    cols_to_keep = ['idade', 'count']
    if 'category' in df_std.columns:
        cols_to_keep.append('category')
    
    df_std = df_std[cols_to_keep].reset_index(drop=True)
    df_std = df_std.dropna()
    
    return df_std


def calculate_mx(deaths_data, population_data, deaths_age_col=None, deaths_count_col=None,
                 pop_age_col=None, pop_count_col=None):
    """
    Calculate mortality rate (mx) by age group.
    
    mx = D/N where:
    - D = number of deaths in age group
    - N = population in that age group
    
    Parameters:
    - deaths_data: DataFrame with deaths by age
    - population_data: DataFrame with population by age
    - deaths_age_col: Age column name in deaths_data (auto-detect if None)
    - deaths_count_col: Count column name in deaths_data (auto-detect if None)
    - pop_age_col: Age column name in population_data (auto-detect if None)
    - pop_count_col: Count column name in population_data (auto-detect if None)
    
    Returns:
    - DataFrame with columns: ['idade', 'deaths', 'population', 'mx']
    """
    
    # Standardize both datasets
    deaths_std = standardize_data(deaths_data, age_col=deaths_age_col, count_col=deaths_count_col)
    population_std = standardize_data(population_data, age_col=pop_age_col, count_col=pop_count_col)
    
    # Rename count columns to be descriptive
    deaths_std.rename(columns={'count': 'deaths'}, inplace=True)
    population_std.rename(columns={'count': 'population'}, inplace=True)
    
    # Merge on idade
    merged = pd.merge(deaths_std, population_std, on='idade', how='inner')
    
    # Calculate mortality rate
    merged['mx'] = merged['deaths'] / merged['population']
    
    return merged[['idade', 'deaths', 'population', 'mx']]


def deaths_by_age_group(data, age_col='idade', category_col=None, category_labels=None, 
                        format='auto', fill_na=True):
    """
    Calculate total deaths by age and optional subgroup/category.
    
    Parameters:
    - data: Input DataFrame with death records
    - age_col: Column name for age (default: 'idade')
    - category_col: Column name for category/subgroup (e.g., 'raca_cor', 'sexo', 'escolaridade')
    - category_labels: Dict to map category codes to labels
    - format: 'auto', 'long', or 'pivot'
    - fill_na: If True, fill NaN values with 0 in pivot format
    
    Returns:
    - DataFrame with deaths aggregated by age (and category if provided)
    """
    
    df = data.copy()
    
    # Standardize age column
    df[age_col] = pd.to_numeric(df[age_col], errors='coerce').fillna(0).astype(int)
    
    # Case 1: Only age grouping (no category)
    if category_col is None:
        deaths_age = df.groupby(age_col).size().reset_index(name='deaths')
        deaths_age.columns = ['idade', 'deaths']
        return deaths_age.sort_values('idade').reset_index(drop=True)
    
    # Case 2: Age and category grouping
    df[category_col] = df[category_col].fillna(0)
    if df[category_col].dtype == 'float64':
        df[category_col] = df[category_col].astype(int).astype(str)
    else:
        df[category_col] = df[category_col].astype(str).str.strip()
    
    # Group by age and category
    deaths_grouped = df.groupby([age_col, category_col]).size().reset_index(name='deaths')
    deaths_grouped.columns = ['idade', 'category_code', 'deaths']
    
    # Apply category labels if provided
    if category_labels:
        normalized_labels = {str(k): v for k, v in category_labels.items()}
        deaths_grouped['category_name'] = deaths_grouped['category_code'].map(normalized_labels)
        deaths_grouped = deaths_grouped.dropna(subset=['category_name'])
    else:
        deaths_grouped['category_name'] = deaths_grouped['category_code']
    
    # Return in requested format
    if format == 'pivot' or (format == 'auto' and category_col):
        pivot_df = deaths_grouped.pivot_table(
            index='idade',
            columns='category_name',
            values='deaths',
            aggfunc='sum'
        )
        if fill_na:
            pivot_df = pivot_df.fillna(0).astype(int)
        return pivot_df.reset_index()
    
    else:  # format == 'long'
        return deaths_grouped[['idade', 'category_name', 'deaths']].sort_values(['idade', 'category_name']).reset_index(drop=True)


# ==================== SUMMARY STATISTICS FUNCTIONS ====================

def generate_summary_stats(df, name="Dataset"):
    """
    Generate summary statistics for a mortality dataset.
    
    Parameters:
    - df: DataFrame with 'idade' and mortality data columns
    - name: Name of the dataset
    
    Returns:
    - Dictionary with summary statistics
    """
    # Find all numeric columns except 'idade'
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    numeric_cols = [col for col in numeric_cols if col != 'idade']
    
    summary = {
        'Dataset': name,
        'Total_Deaths': df[numeric_cols].sum().sum(),
        'Age_Range_Min': df['idade'].min(),
        'Age_Range_Max': df['idade'].max(),
        'Unique_Ages': df['idade'].nunique(),
        'Mean_Age_at_Death': (df['idade'] * df[numeric_cols].sum(axis=1)).sum() / df[numeric_cols].sum().sum(),
    }
    
    # Add category-specific statistics if multiple columns
    if len(numeric_cols) > 1:
        for col in numeric_cols:
            summary[f'{col}_Deaths'] = df[col].sum()
            summary[f'{col}_Percent'] = (df[col].sum() / df[numeric_cols].sum().sum()) * 100
    
    return summary


# ==================== ELEITORADO PIPELINE ====================

# SIM sex codes: 1=Masculino, 2=Feminino
GENDER_MAP = {"MASCULINO": 1, "FEMININO": 2}
# SIM race codes: 1=Branca, 2=Preta, 3=Amarela, 4=Parda, 5=Indígena
RACE_MAP = {"Branca": 1, "Preta": 2, "Amarela": 3, "Parda": 4, "Indígena": 5}


def load_eleitorado(path: Path) -> pd.DataFrame:
    """
    Load and clean one ELEITORADO CSV file.

    DS_FAIXA_ETARIA parsing:
      "N anos"           → int N
      "100 anos ou mais" → 100
      other              → dropped (count logged)

    Returns DataFrame with columns:
        ['SG_UF', 'idade', 'DS_GENERO', 'DS_COR_RACA', 'qt_eleitores']
    """
    df = pd.read_csv(path, dtype={"DS_FAIXA_ETARIA": str})
    original_len = len(df)

    def parse_age(s):
        if pd.isna(s):
            return None
        s = s.strip()
        if s == "100 anos ou mais":
            return 100
        m = re.match(r"^(\d+)\s+anos?$", s, re.IGNORECASE)
        return int(m.group(1)) if m else None

    df["idade"] = df["DS_FAIXA_ETARIA"].map(parse_age)
    dropped = df["idade"].isna().sum()
    if dropped:
        sample = df.loc[df["idade"].isna(), "DS_FAIXA_ETARIA"].dropna().unique()[:5].tolist()
        logger.warning(
            f"load_eleitorado: dropped {dropped}/{original_len} rows with unparseable DS_FAIXA_ETARIA "
            f"(samples: {sample})"
        )
    df = df.dropna(subset=["idade"]).copy()
    df["idade"] = df["idade"].astype(int)

    keep = ["SG_UF", "idade", "DS_GENERO", "DS_COR_RACA", "qt_eleitores"]
    return df[keep].reset_index(drop=True)


def find_matched_years(microdados_dir: Path, eleitorado_dir: Path) -> dict:
    """
    Find years with both a SIM-DATASUS-{year}.csv and an eleitorado_{year}.csv.
    Returns {year: (deaths_path, eleitorado_path)}.
    """
    deaths_years = {}
    for f in microdados_dir.glob("SIM-DATASUS-*.csv"):
        m = re.search(r"(\d{4})", f.stem)
        if m:
            deaths_years[int(m.group(1))] = f

    edf_years = {}
    for f in eleitorado_dir.glob("eleitorado_*.csv"):
        m = re.search(r"(\d{4})", f.stem)
        if m:
            edf_years[int(m.group(1))] = f

    matched = {
        year: (deaths_years[year], edf_years[year])
        for year in sorted(set(deaths_years) & set(edf_years))
    }

    missing_deaths = sorted(set(edf_years) - set(deaths_years))
    missing_edf = sorted(set(deaths_years) - set(edf_years))
    if missing_deaths:
        logger.warning(f"Eleitorado years with no matching deaths file: {missing_deaths}")
    if missing_edf:
        logger.warning(f"Deaths years with no matching eleitorado file: {missing_edf}")
    if not matched:
        logger.warning("No matching year pairs found — nothing to process")

    return matched


def run_eleitorado_mortality_analysis(
    microdados_dir: Path = MICRODADOS_DIR,
    eleitorado_dir: Path = ELEITORADO_DIR,
    deaths_uf_col: str | None = None,
):
    """
    Compute mx curves for every year that has both a SIM-DATASUS and ELEITORADO file.

    File patterns expected:
      microdados_dir/SIM-DATASUS-{year}.csv
      eleitorado_dir/eleitorado_{year}.csv

    Outputs data/processed/{year}/{category}/mx_{label}.csv with columns
    ['idade', 'deaths', 'population', 'mx'] for each matched year.

    Categories produced:
      total/           — all deaths, all voters
      genero/          — one curve per DS_GENERO (MASCULINO, FEMININO)
      raca_cor/        — one curve per DS_COR_RACA (skips "Não informado")
      uf/              — one curve per SG_UF (only if deaths_uf_col is given)
    """
    logger.info("=" * 70)
    logger.info("ELEITORADO MORTALITY PIPELINE - START")
    logger.info("=" * 70)

    matched = find_matched_years(microdados_dir, eleitorado_dir)
    if not matched:
        return {}

    all_results = {}

    for year, (deaths_path, edf_path) in matched.items():
        logger.info(f"\n── Year {year} ─────────────────────────────────────────")
        logger.info(f"   deaths:     {deaths_path}")
        logger.info(f"   eleitorado: {edf_path}")

        deaths_data = pd.read_csv(deaths_path)
        logger.info(f"   ✓ deaths loaded: {deaths_data.shape}")

        edf = load_eleitorado(edf_path)
        logger.info(f"   ✓ eleitorado loaded: {edf.shape}")

        if edf.empty:
            logger.warning(f"   ✗ year {year} skipped — eleitorado has no parseable age rows")
            continue

        out_base = OUTPUT_DIR / str(year)
        year_results = {}

        # Normalise raca_cor to int for reliable comparison regardless of source dtype
        has_raca = "raca_cor" in deaths_data.columns
        if has_raca:
            deaths_data["raca_cor"] = pd.to_numeric(deaths_data["raca_cor"], errors="coerce")

        has_sexo = "sexo" in deaths_data.columns
        if has_sexo:
            deaths_data["sexo"] = pd.to_numeric(deaths_data["sexo"], errors="coerce")

        def mx_curve(deaths_mask, exp_df):
            d = deaths_data if deaths_mask is None else deaths_data[deaths_mask]
            d_agg = deaths_by_age_group(d, age_col="idade")
            if d_agg.empty or exp_df.empty:
                return None
            return calculate_mx(
                deaths_data=d_agg,
                population_data=exp_df,
                deaths_age_col="idade",
                deaths_count_col="deaths",
                pop_age_col="idade",
                pop_count_col="qt_eleitores",
            )

        def save(df, *path_parts):
            out = out_base.joinpath(*path_parts)
            out.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(out, index=False)
            logger.info(f"    ✓ saved {out}")

        # ── Total ──────────────────────────────────────────────────────────
        exp_total = edf.groupby("idade", as_index=False)["qt_eleitores"].sum()
        mx_total = mx_curve(None, exp_total)
        if mx_total is not None:
            year_results["total"] = mx_total
            save(mx_total, "total", "mx_total.csv")
        else:
            logger.warning(f"    ✗ total: no overlapping ages")

        # ── Gender ─────────────────────────────────────────────────────────
        year_results["by_gender"] = {}
        for gender_label, sexo_code in GENDER_MAP.items():
            exp_g = (
                edf[edf["DS_GENERO"] == gender_label]
                .groupby("idade", as_index=False)["qt_eleitores"].sum()
            )
            d_mask = (deaths_data["sexo"] == sexo_code) if has_sexo else None
            mx = mx_curve(d_mask, exp_g)
            if mx is not None:
                year_results["by_gender"][gender_label] = mx
                safe = gender_label.lower().replace(" ", "_")
                save(mx, "genero", f"mx_{safe}.csv")
            else:
                logger.warning(f"    ✗ gender '{gender_label}': no overlapping ages")

        # ── Race ───────────────────────────────────────────────────────────
        year_results["by_race"] = {}
        valid_race_labels = set(RACE_MAP.keys())
        edf_known_race = edf[edf["DS_COR_RACA"].isin(valid_race_labels)]
        if edf_known_race.empty:
            logger.warning(f"    ✗ race skipped — no recognised DS_COR_RACA values (found: {edf['DS_COR_RACA'].unique()[:5].tolist()})")
        for race_label, raca_code in RACE_MAP.items():
            exp_r = (
                edf_known_race[edf_known_race["DS_COR_RACA"] == race_label]
                .groupby("idade", as_index=False)["qt_eleitores"].sum()
            )
            d_mask = (deaths_data["raca_cor"] == raca_code) if has_raca else None
            mx = mx_curve(d_mask, exp_r)
            if mx is not None:
                year_results["by_race"][race_label] = mx
                safe = race_label.lower().replace(" ", "_")
                save(mx, "raca_cor", f"mx_{safe}.csv")
            else:
                logger.warning(f"    ✗ race '{race_label}': no overlapping ages")

        # ── UF ─────────────────────────────────────────────────────────────
        year_results["by_uf"] = None
        if deaths_uf_col and deaths_uf_col in deaths_data.columns:
            year_results["by_uf"] = {}
            for uf in sorted(edf["SG_UF"].unique()):
                exp_uf = (
                    edf[edf["SG_UF"] == uf]
                    .groupby("idade", as_index=False)["qt_eleitores"].sum()
                )
                d_mask = deaths_data[deaths_uf_col] == uf
                mx = mx_curve(d_mask, exp_uf)
                if mx is not None:
                    year_results["by_uf"][uf] = mx
                    save(mx, "uf", f"mx_{uf.lower()}.csv")
        elif deaths_uf_col:
            logger.warning(f"deaths_uf_col='{deaths_uf_col}' not in deaths columns — UF curves skipped")

        all_results[year] = year_results

    logger.info("\n✓ Eleitorado pipeline complete")
    return all_results


# ==================== ENTRY POINT ====================

if __name__ == "__main__":
    logger.info(f"Started at: {datetime.now()}")

    results = run_eleitorado_mortality_analysis(
        microdados_dir=MICRODADOS_DIR,
        eleitorado_dir=ELEITORADO_DIR,
        deaths_uf_col="sigla_uf",
    )

    logger.info(f"\nCompleted at: {datetime.now()}")
