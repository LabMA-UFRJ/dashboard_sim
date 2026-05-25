"""
Mortality Analysis and mx Calculation Pipeline
===============================================

This module provides a complete pipeline for:
1. Loading death records and population data
2. Standardizing data formats
3. Calculating mortality rates (mx) by age and demographic categories
4. Generating summary statistics
5. Exporting results to CSV for visualization

Author: Mortality Analysis System
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
# Update these paths to your actual data locations

DEATHS_DATA_PATH = "//Projetos2/Wrk/SIM-DATASUS/MICRODADOS/SIM-DATASUS-2010.csv"
POPULATION_DATA_PATH = "//Projetos2/Wrk/SIM-DATASUS/IBGE/censo2010.csv"

# Extract source names from file paths
DEATHS_SOURCE = Path(DEATHS_DATA_PATH).stem  # "SIM-DATASUS"
POPULATION_SOURCE = Path(POPULATION_DATA_PATH).stem  # "censo2022"

# Extract population source name and year from filename
def extract_source_and_year(filename):
    """Extract source name and year from filename like 'censo2022' or 'ibge2010'"""
    match = re.match(r'([a-zA-Z]+)(\d{4})', filename)
    if match:
        source_name, year = match.groups()
        source_name = source_name.capitalize()  # "censo" -> "Censo"
        return source_name, year
    return filename, ""

POP_SOURCE_NAME, POP_YEAR = extract_source_and_year(POPULATION_SOURCE)

# Output directory structure: output/{population_source}/{year}/{category}/
OUTPUT_DIR = Path("./output")
OUTPUT_BASE = OUTPUT_DIR / POP_SOURCE_NAME / POP_YEAR

# Create category subdirectories
DEATHS_DIR = OUTPUT_BASE / "deaths"
MX_DIR = OUTPUT_BASE / "mx"
SUMMARY_DIR = OUTPUT_BASE / "summary"

DEATHS_DIR.mkdir(parents=True, exist_ok=True)
MX_DIR.mkdir(parents=True, exist_ok=True)
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

logger.info(f"Output directory: {OUTPUT_DIR}")
logger.info(f"Deaths source: {DEATHS_SOURCE}")
logger.info(f"Population source: {POPULATION_SOURCE}")
logger.info(f"Population source name: {POP_SOURCE_NAME}, Year: {POP_YEAR}")
logger.info(f"Output path: {OUTPUT_BASE}")


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


# ==================== HELPER FUNCTIONS ====================

def get_output_filepath(category, base_name, suffix=""):
    """
    Generate output filepath with organized directory structure.
    
    Parameters:
    - category: Category type ('deaths', 'mx', or 'summary')
    - base_name: Base filename (e.g., "01_deaths_by_age")
    - suffix: Optional additional suffix (e.g., "masculino")
    
    Returns:
    - Full filepath in organized structure
    """
    # Select directory based on category
    if category == 'deaths':
        output_dir = DEATHS_DIR
    elif category == 'mx':
        output_dir = MX_DIR
    elif category == 'summary':
        output_dir = SUMMARY_DIR
    else:
        output_dir = OUTPUT_BASE
    
    # Generate filename with sources
    if suffix:
        filename = f"{base_name}_{suffix}_{DEATHS_SOURCE}_{POPULATION_SOURCE}.csv"
    else:
        filename = f"{base_name}_{DEATHS_SOURCE}_{POPULATION_SOURCE}.csv"
    
    return output_dir / filename


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


# ==================== MAIN ANALYSIS PIPELINE ====================

def run_mortality_analysis():
    """
    Execute the complete mortality analysis pipeline.
    """
    
    logger.info("="*70)
    logger.info("MORTALITY ANALYSIS PIPELINE - START")
    logger.info("="*70)
    
    try:
        # Load data
        logger.info(f"\nLoading deaths data from: {DEATHS_DATA_PATH}")
        deaths_data = pd.read_csv(DEATHS_DATA_PATH)
        logger.info(f"✓ Deaths data loaded: {deaths_data.shape[0]} records, {deaths_data.shape[1]} columns")
        
        logger.info(f"\nLoading population data from: {POPULATION_DATA_PATH}")
        population_data = pd.read_csv(POPULATION_DATA_PATH)
        logger.info(f"✓ Population data loaded: {population_data.shape[0]} records, {population_data.shape[1]} columns")
        
        # Dictionary to store all results
        results = {}
        
        # ==================== 1. DEATHS BY AGE ONLY ====================
        logger.info("\n" + "="*70)
        logger.info("CALCULATING: Deaths by Age")
        logger.info("="*70)
        
        deaths_by_age = deaths_by_age_group(deaths_data, age_col='idade')
        results['deaths_by_age'] = deaths_by_age
        
        output_file = get_output_filepath("deaths", "01_deaths_by_age")
        deaths_by_age.to_csv(output_file, index=False)
        logger.info(f"✓ Saved to: {output_file}")
        logger.info(f"  Total deaths: {deaths_by_age['deaths'].sum():,}")
        logger.info(f"  Age range: {deaths_by_age['idade'].min()} - {deaths_by_age['idade'].max()}")
        
        # ==================== 2. DEATHS BY AGE AND SEX ====================
        logger.info("\n" + "="*70)
        logger.info("CALCULATING: Deaths by Age and Sex")
        logger.info("="*70)
        
        deaths_by_sex = deaths_by_age_group(
            deaths_data,
            age_col='idade',
            category_col='sexo',
            category_labels=DICTIONARY_LABELS['sexo'],
            format='pivot',
            fill_na=True
        )
        results['deaths_by_sex'] = deaths_by_sex
        
        output_file = get_output_filepath("deaths", "02_deaths_by_age_and_sex")
        deaths_by_sex.to_csv(output_file, index=False)
        logger.info(f"✓ Saved to: {output_file}")
        logger.info(f"  Shape: {deaths_by_sex.shape}")
        logger.info(f"  Categories: {deaths_by_sex.columns.tolist()}")
        
        # ==================== 3. DEATHS BY AGE AND RACE ====================
        logger.info("\n" + "="*70)
        logger.info("CALCULATING: Deaths by Age and Race/Color")
        logger.info("="*70)
        
        deaths_by_race = deaths_by_age_group(
            deaths_data,
            age_col='idade',
            category_col='raca_cor',
            category_labels=DICTIONARY_LABELS['raca_cor'],
            format='pivot',
            fill_na=True
        )
        results['deaths_by_race'] = deaths_by_race
        
        output_file = get_output_filepath("deaths", "03_deaths_by_age_and_race")
        deaths_by_race.to_csv(output_file, index=False)
        logger.info(f"✓ Saved to: {output_file}")
        logger.info(f"  Shape: {deaths_by_race.shape}")
        logger.info(f"  Categories: {deaths_by_race.columns.tolist()}")
        
        # ==================== 4. DEATHS BY AGE AND EDUCATION ====================
        logger.info("\n" + "="*70)
        logger.info("CALCULATING: Deaths by Age and Education")
        logger.info("="*70)
        
        deaths_by_education = deaths_by_age_group(
            deaths_data,
            age_col='idade',
            category_col='escolaridade',
            category_labels=DICTIONARY_LABELS['escolaridade'],
            format='pivot',
            fill_na=True
        )
        results['deaths_by_education'] = deaths_by_education
        
        output_file = get_output_filepath("deaths", "04_deaths_by_age_and_education")
        deaths_by_education.to_csv(output_file, index=False)
        logger.info(f"✓ Saved to: {output_file}")
        logger.info(f"  Shape: {deaths_by_education.shape}")
        logger.info(f"  Categories: {deaths_by_education.columns.tolist()}")
        
        # ==================== 5. DEATHS BY AGE AND MARITAL STATUS ====================
        logger.info("\n" + "="*70)
        logger.info("CALCULATING: Deaths by Age and Marital Status")
        logger.info("="*70)
        
        deaths_by_marital = deaths_by_age_group(
            deaths_data,
            age_col='idade',
            category_col='estado_civil',
            category_labels=DICTIONARY_LABELS['estado_civil'],
            format='pivot',
            fill_na=True
        )
        results['deaths_by_marital'] = deaths_by_marital
        
        output_file = get_output_filepath("deaths", "05_deaths_by_age_and_marital_status")
        deaths_by_marital.to_csv(output_file, index=False)
        logger.info(f"✓ Saved to: {output_file}")
        logger.info(f"  Shape: {deaths_by_marital.shape}")
        logger.info(f"  Categories: {deaths_by_marital.columns.tolist()}")
        
        # ==================== 6. MORTALITY RATE (mx) - TOTAL ====================
        logger.info("\n" + "="*70)
        logger.info("CALCULATING: Mortality Rate (mx) - Total Population")
        logger.info("="*70)
        
        mx_total = calculate_mx(
            deaths_data=deaths_by_age,
            population_data=population_data,
            deaths_age_col='idade',
            deaths_count_col='deaths',
            pop_age_col='Idade',
            pop_count_col='Total'
        )
        results['mx_total'] = mx_total
        
        output_file = get_output_filepath("mx", "06_mx_total_population")
        mx_total.to_csv(output_file, index=False)
        logger.info(f"✓ Saved to: {output_file}")
        logger.info(f"  Age range: {mx_total['idade'].min()} - {mx_total['idade'].max()}")
        logger.info(f"  Mean mx: {mx_total['mx'].mean():.6f}")
        logger.info(f"  Max mx (at age {mx_total.loc[mx_total['mx'].idxmax(), 'idade']:.0f}): {mx_total['mx'].max():.6f}")
        
        # ==================== 7. MORTALITY RATE (mx) BY SEX ====================
        logger.info("\n" + "="*70)
        logger.info("CALCULATING: Mortality Rate (mx) by Sex")
        logger.info("="*70)
        
        mx_by_sex = {}
        for sex_code, sex_name in DICTIONARY_LABELS['sexo'].items():
            logger.info(f"\n  Processing: {sex_name}")
            
            # Prepare deaths data for this sex
            deaths_sex = deaths_data[deaths_data['sexo'] == float(sex_code)].groupby('idade').size().reset_index(name='deaths')
            deaths_sex.columns = ['idade', 'deaths']
            
            try:
                mx_sex = calculate_mx(
                    deaths_data=deaths_sex,
                    population_data=population_data,
                    deaths_age_col='idade',
                    deaths_count_col='deaths',
                    pop_age_col='Idade',
                    pop_count_col=sex_name
                )
                mx_by_sex[sex_name] = mx_sex
                
                output_file = get_output_filepath("mx", "07_mx_by_sex", sex_name.lower())
                mx_sex.to_csv(output_file, index=False)
                logger.info(f"    ✓ Saved to: {output_file}")
                logger.info(f"    Mean mx: {mx_sex['mx'].mean():.6f}")
            except Exception as e:
                logger.warning(f"    ✗ Could not calculate mx for {sex_name}: {str(e)}")
        
        results['mx_by_sex'] = mx_by_sex
        
        # ==================== 8. MORTALITY RATE (mx) BY RACE ====================
        logger.info("\n" + "="*70)
        logger.info("CALCULATING: Mortality Rate (mx) by Race/Color")
        logger.info("="*70)
        
        mx_by_race = {}
        for race_code, race_name in DICTIONARY_LABELS['raca_cor'].items():
            logger.info(f"\n  Processing: {race_name}")
            
            # Prepare deaths data for this race
            deaths_race = deaths_data[deaths_data['raca_cor'] == float(race_code)].groupby('idade').size().reset_index(name='deaths')
            deaths_race.columns = ['idade', 'deaths']
            
            try:
                mx_race = calculate_mx(
                    deaths_data=deaths_race,
                    population_data=population_data,
                    deaths_age_col='idade',
                    deaths_count_col='deaths',
                    pop_age_col='Idade',
                    pop_count_col=race_name
                )
                mx_by_race[race_name] = mx_race
                
                output_file = get_output_filepath("mx", "08_mx_by_race", race_name.lower())
                mx_race.to_csv(output_file, index=False)
                logger.info(f"    ✓ Saved to: {output_file}")
                logger.info(f"    Mean mx: {mx_race['mx'].mean():.6f}")
            except Exception as e:
                logger.warning(f"    ✗ Could not calculate mx for {race_name}: {str(e)}")
        
        results['mx_by_race'] = mx_by_race
        
        # ==================== 9. SUMMARY STATISTICS ====================
        logger.info("\n" + "="*70)
        logger.info("GENERATING: Summary Statistics")
        logger.info("="*70)
        
        summary_list = []
        
        for dataset_name, dataset_df in results.items():
            if dataset_name.startswith('deaths_by_'):
                try:
                    summary = generate_summary_stats(dataset_df, dataset_name)
                    summary_list.append(summary)
                    logger.info(f"  ✓ {dataset_name}")
                except Exception as e:
                    logger.warning(f"  ✗ {dataset_name}: {str(e)}")
        
        if summary_list:
            summary_df = pd.DataFrame(summary_list)
            output_file = get_output_filepath("summary", "09_summary_statistics")
            summary_df.to_csv(output_file, index=False)
            logger.info(f"\n✓ Summary statistics saved to: {output_file}")
        
        # ==================== FINAL REPORT ====================
        logger.info("\n" + "="*70)
        logger.info("ANALYSIS COMPLETE")
        logger.info("="*70)
        logger.info(f"\nOutput directory: {OUTPUT_DIR.absolute()}")
        logger.info(f"Files created:")
        
        for i, file in enumerate(sorted(OUTPUT_DIR.glob("*.csv")), 1):
            logger.info(f"  {i}. {file.name}")
        
        logger.info("\n✓ All results saved and ready for visualization!")
        
        return results
        
    except Exception as e:
        logger.error(f"\n✗ ANALYSIS FAILED: {str(e)}", exc_info=True)
        raise


# ==================== ENTRY POINT ====================

if __name__ == "__main__":
    logger.info(f"Started at: {datetime.now()}")
    
    results = run_mortality_analysis()
    
    logger.info(f"\nCompleted at: {datetime.now()}")
