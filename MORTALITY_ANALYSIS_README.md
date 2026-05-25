# Mortality Analysis and mx Calculation Pipeline

## Overview

This Python script provides a complete, generalized pipeline for analyzing mortality data and calculating mortality rates (mx). It automatically handles data standardization, aggregation, and mx calculations for any input data format.

**File:** `calculate_mortality_analysis.py`

## Features

✓ **Generalized Data Processing** - Works with any demographic dataset format
✓ **Automatic Column Detection** - Auto-detects age and count columns
✓ **Multi-Category Analysis** - Calculates statistics by sex, race/color, education, marital status
✓ **Mortality Rate Calculation** - Computes mx (deaths/population) for all categories
✓ **CSV Export** - Saves all results in organized CSV files
✓ **Comprehensive Logging** - Detailed progress tracking and error reporting

## Input Data Requirements

### Deaths Data
- Column: `idade` (age)
- Required categories: `sexo`, `raca_cor`, `escolaridade`, `estado_civil`
- Format: Individual death records

### Population Data
- Column: `Idade` (age)
- Required columns: `Total`, `Masculino`, `Feminino`, `Branca`, `Preta`, `Amarela`, `Parda`, `Indígena`
- Format: Aggregated by age group and demographic categories

## Configuration

Edit the data paths in the script:

```python
DEATHS_DATA_PATH = "//Projetos2/Wrk/SIM-DATASUS/MICRODADOS/SIM-DATASUS-2020.csv"
POPULATION_DATA_PATH = "//Projetos2/Wrk/SIM-DATASUS/IBGE/censo2022.csv"
OUTPUT_DIR = Path("./output")  # Output directory for CSV files
```

## Usage

### Option 1: Run directly from terminal

```bash
python calculate_mortality_analysis.py
```

### Option 2: Import in another Python script

```python
from calculate_mortality_analysis import run_mortality_analysis, calculate_mx, deaths_by_age_group

# Run the complete pipeline
results = run_mortality_analysis()

# Or use individual functions
mx_result = calculate_mx(deaths_df, population_df)
deaths_pivot = deaths_by_age_group(data, category_col='sexo', format='pivot')
```

## Output Files

The script generates 9 CSV files in the `output/` directory:

### 1. Deaths Aggregations
- **01_deaths_by_age.csv** - Total deaths by age only
  - Columns: `idade`, `deaths`

- **02_deaths_by_age_and_sex.csv** - Deaths by age × sex
  - Columns: `idade`, `Masculino`, `Feminino`

- **03_deaths_by_age_and_race.csv** - Deaths by age × race/color
  - Columns: `idade`, `Branca`, `Preta`, `Amarela`, `Parda`, `Indígena`

- **04_deaths_by_age_and_education.csv** - Deaths by age × education level
  - Columns: `idade`, `Nenhuma`, `1 a 3 anos`, `4 a 7 anos`, `8 a 11 anos`, `12 anos ou mais`

- **05_deaths_by_age_and_marital_status.csv** - Deaths by age × marital status
  - Columns: `idade`, `Solteiro(a)`, `Casado(a)`, `Viúvo(a)`, `Divorciado(a)`, `União Consensual`

### 2. Mortality Rates (mx)
- **06_mx_total_population.csv** - Mortality rate for total population
  - Columns: `idade`, `deaths`, `population`, `mx`

- **07_mx_by_sex_*.csv** - Mortality rate by sex (Masculino, Feminino)
  - Columns: `idade`, `deaths`, `population`, `mx`

- **08_mx_by_race_*.csv** - Mortality rate by race/color (Branca, Preta, Amarela, Parda, Indígena)
  - Columns: `idade`, `deaths`, `population`, `mx`

### 3. Summary Statistics
- **09_summary_statistics.csv** - Summary statistics for each dataset
  - Total deaths, age range, mean age at death, percentage breakdown

## Core Functions

### `deaths_by_age_group(data, age_col='idade', category_col=None, category_labels=None, format='auto', fill_na=True)`

Calculates deaths by age and optional category.

```python
# Deaths by age only
df = deaths_by_age_group(data)

# Deaths by age and sex (pivot format)
df = deaths_by_age_group(
    data,
    category_col='sexo',
    category_labels={'1': 'Masculino', '2': 'Feminino'},
    format='pivot'
)

# Deaths by age and race (long format)
df = deaths_by_age_group(
    data,
    category_col='raca_cor',
    category_labels={'1': 'Branca', '2': 'Preta', ...},
    format='long'
)
```

### `calculate_mx(deaths_data, population_data, deaths_age_col=None, deaths_count_col=None, pop_age_col=None, pop_count_col=None)`

Calculates mortality rate (mx = deaths/population) by age.

```python
mx = calculate_mx(
    deaths_data=deaths_df,
    population_data=population_df,
    deaths_age_col='idade',
    deaths_count_col='deaths',
    pop_age_col='Idade',
    pop_count_col='Total'
)
```

### `standardize_data(df, age_col=None, count_col=None, category_col=None)`

Standardizes any demographic data to common format with auto-detection of columns.

```python
std_data = standardize_data(df)  # Auto-detects columns
std_data = standardize_data(df, age_col='age_col_name', count_col='count_col_name')
```

## Example Output

When you run the script, you'll see output like:

```
INFO - ======================================================================
INFO - MORTALITY ANALYSIS PIPELINE - START
INFO - ======================================================================
INFO - Loading deaths data from: //Projetos2/Wrk/SIM-DATASUS/MICRODADOS/SIM-DATASUS-2020.csv
INFO - ✓ Deaths data loaded: 1556824 records, 23 columns
INFO - Loading population data from: //Projetos2/Wrk/SIM-DATASUS/IBGE/censo2022.csv
INFO - ✓ Population data loaded: 101 records, 7 columns
INFO - 
INFO - ======================================================================
INFO - CALCULATING: Deaths by Age
INFO - ======================================================================
INFO - ✓ Saved to: ./output/01_deaths_by_age.csv
INFO -   Total deaths: 1,556,824
INFO -   Age range: 0 - 125
...
```

## Use Cases

### 1. Generate Visualizations
Load the output CSVs into your preferred visualization tool (Matplotlib, Plotly, Tableau, etc.)

```python
import matplotlib.pyplot as plt
import pandas as pd

mx_data = pd.read_csv('output/06_mx_total_population.csv')
plt.plot(mx_data['idade'], mx_data['mx'])
plt.xlabel('Age')
plt.ylabel('Mortality Rate (mx)')
plt.show()
```

### 2. Statistical Analysis
Use the mx values for comparative analysis between groups

```python
mx_male = pd.read_csv('output/07_mx_by_sex_masculino.csv')
mx_female = pd.read_csv('output/07_mx_by_sex_feminino.csv')

# Compare mortality rates
comparison = mx_male.merge(mx_female, on='idade', suffixes=('_male', '_female'))
comparison['mx_difference'] = comparison['mx_male'] - comparison['mx_female']
```

### 3. Data Export
All results are ready for import into:
- Power BI
- Tableau
- Excel/Google Sheets
- Python statistical libraries (scipy, statsmodels)
- R analysis tools

## Troubleshooting

### Issue: "Could not find age column"
**Solution:** Ensure your data has an 'idade' or 'Idade' column, or specify it manually:
```python
deaths_by_age_group(data, age_col='your_age_column_name')
```

### Issue: Empty results for a category
**Solution:** Check if the category column exists and is named correctly:
```python
print(data.columns)  # List all columns
print(data['raca_cor'].value_counts())  # Check values
```

### Issue: File not found
**Solution:** Verify data paths are correct and files exist:
```bash
# Windows
dir "//Projetos2/Wrk/SIM-DATASUS/MICRODADOS/"

# Linux/Mac
ls "//Projetos2/Wrk/SIM-DATASUS/MICRODADOS/"
```

## Performance Notes

- **Large datasets:** Processing ~1.5M death records typically takes 10-30 seconds
- **Memory:** Requires ~200-500MB RAM for typical datasets
- **Output:** All 9 CSV files total ~5-10MB disk space

## Dependencies

```
pandas>=1.0.0
numpy>=1.18.0
```

Install with: `pip install pandas numpy`

## Author

Mortality Analysis System
Date: 2026

## License

Project-specific use only
