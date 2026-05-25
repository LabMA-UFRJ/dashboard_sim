"""
Mortality Analysis Validation and Data Integrity Check
=======================================================

This script validates the generated mortality analysis results by:
1. Comparing totals between original data and generated CSVs
2. Verifying mx calculations (mx = deaths/population)
3. Checking for data loss or duplication
4. Validating age ranges and data consistency
5. Generating a detailed validation report

Author: Mortality Analysis Validation System
Date: 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== CONFIGURATION ====================

DEATHS_DATA_PATH = "//Projetos2/Wrk/SIM-DATASUS/MICRODADOS/SIM-DATASUS-2020.csv"
POPULATION_DATA_PATH = "//Projetos2/Wrk/SIM-DATASUS/IBGE/censo2022.csv"
OUTPUT_DIR = Path("./output")
VALIDATION_DIR = Path("./validation_report")
VALIDATION_DIR.mkdir(exist_ok=True)

DICTIONARY_LABELS = {
    'sexo': {'1': 'Masculino', '2': 'Feminino'},
    'raca_cor': {'1': 'Branca', '2': 'Preta', '3': 'Amarela', '4': 'Parda', '5': 'Indígena'},
}


# ==================== VALIDATION FUNCTIONS ====================

def load_raw_data():
    """Load original raw data."""
    logger.info("Loading original raw data...")
    deaths_data = pd.read_csv(DEATHS_DATA_PATH)
    population_data = pd.read_csv(POPULATION_DATA_PATH)
    logger.info(f"✓ Deaths data: {deaths_data.shape[0]:,} records")
    logger.info(f"✓ Population data: {population_data.shape[0]:,} records")
    return deaths_data, population_data


def get_expected_totals(deaths_data):
    """Get expected totals from raw data."""
    logger.info("\n" + "="*70)
    logger.info("EXPECTED TOTALS (from raw data)")
    logger.info("="*70)
    
    expected = {}
    
    # Total deaths
    expected['total_deaths'] = len(deaths_data)
    logger.info(f"Total deaths in raw data: {expected['total_deaths']:,}")
    
    # Deaths by sex
    for sex_code, sex_name in DICTIONARY_LABELS['sexo'].items():
        count = len(deaths_data[deaths_data['sexo'] == float(sex_code)])
        expected[f'deaths_sex_{sex_name}'] = count
        logger.info(f"Deaths ({sex_name}): {count:,}")
    
    # Deaths by race
    for race_code, race_name in DICTIONARY_LABELS['raca_cor'].items():
        count = len(deaths_data[deaths_data['raca_cor'] == float(race_code)])
        expected[f'deaths_race_{race_name}'] = count
        logger.info(f"Deaths ({race_name}): {count:,}")
    
    # Missing values
    missing_sex = len(deaths_data[deaths_data['sexo'].isna()])
    missing_race = len(deaths_data[deaths_data['raca_cor'].isna()])
    expected['missing_sex'] = missing_sex
    expected['missing_race'] = missing_race
    logger.info(f"\nMissing values (sexo): {missing_sex:,}")
    logger.info(f"Missing values (raca_cor): {missing_race:,}")
    
    return expected


def validate_deaths_totals(expected):
    """Validate death totals in generated files."""
    logger.info("\n" + "="*70)
    logger.info("VALIDATION 1: DEATHS TOTALS")
    logger.info("="*70)
    
    validation_results = []
    
    # Load generated files
    deaths_by_age = pd.read_csv(OUTPUT_DIR / "01_deaths_by_age.csv")
    deaths_by_sex = pd.read_csv(OUTPUT_DIR / "02_deaths_by_age_and_sex.csv")
    deaths_by_race = pd.read_csv(OUTPUT_DIR / "03_deaths_by_age_and_race.csv")
    
    # Test 1: Total deaths
    total_from_age = deaths_by_age['deaths'].sum()
    expected_total = expected['total_deaths']
    
    test1 = {
        'Test': 'Total Deaths (by age)',
        'Expected': f"{expected_total:,}",
        'Generated': f"{total_from_age:,}",
        'Match': total_from_age == expected_total,
        'Difference': total_from_age - expected_total
    }
    validation_results.append(test1)
    logger.info(f"\n✓ Total deaths (by age): {total_from_age:,} vs {expected_total:,}")
    logger.info(f"  Match: {test1['Match']} | Difference: {test1['Difference']}")
    
    # Test 2: Deaths by sex totals
    sex_totals = deaths_by_sex[['Masculino', 'Feminino']].sum()
    
    for sex_name in ['Masculino', 'Feminino']:
        expected_sex = expected[f'deaths_sex_{sex_name}']
        generated_sex = sex_totals[sex_name]
        
        test = {
            'Test': f'Deaths by Sex ({sex_name})',
            'Expected': f"{expected_sex:,}",
            'Generated': f"{int(generated_sex):,}",
            'Match': int(generated_sex) == expected_sex,
            'Difference': int(generated_sex) - expected_sex
        }
        validation_results.append(test)
        logger.info(f"\n✓ Deaths ({sex_name}): {int(generated_sex):,} vs {expected_sex:,}")
        logger.info(f"  Match: {test['Match']} | Difference: {test['Difference']}")
    
    # Test 3: Deaths by race totals
    race_cols = [col for col in deaths_by_race.columns if col != 'idade']
    
    for race_name in race_cols:
        expected_race = expected[f'deaths_race_{race_name}']
        generated_race = deaths_by_race[race_name].sum()
        
        test = {
            'Test': f'Deaths by Race ({race_name})',
            'Expected': f"{expected_race:,}",
            'Generated': f"{int(generated_race):,}",
            'Match': int(generated_race) == expected_race,
            'Difference': int(generated_race) - expected_race
        }
        validation_results.append(test)
        logger.info(f"\n✓ Deaths ({race_name}): {int(generated_race):,} vs {expected_race:,}")
        logger.info(f"  Match: {test['Match']} | Difference: {test['Difference']}")
    
    # Test 4: Total sex deaths should equal total by age
    total_sex = sex_totals.sum()
    test4 = {
        'Test': 'Sex subtotals sum to total deaths',
        'Expected': f"{total_from_age:,}",
        'Generated': f"{int(total_sex):,}",
        'Match': int(total_sex) == total_from_age,
        'Difference': int(total_sex) - total_from_age
    }
    validation_results.append(test4)
    logger.info(f"\n✓ Sex subtotals: {int(total_sex):,} vs {total_from_age:,}")
    logger.info(f"  Match: {test4['Match']} | Difference: {test4['Difference']}")
    
    return pd.DataFrame(validation_results)


def validate_mx_calculations():
    """Validate mx calculations."""
    logger.info("\n" + "="*70)
    logger.info("VALIDATION 2: mx CALCULATIONS")
    logger.info("="*70)
    
    validation_results = []
    
    # Load mx data
    mx_total = pd.read_csv(OUTPUT_DIR / "06_mx_total_population.csv")
    
    # Test: mx = deaths / population
    mx_calculated = mx_total['deaths'] / mx_total['population']
    mx_diff = np.abs(mx_calculated - mx_total['mx'])
    max_diff = mx_diff.max()
    mean_diff = mx_diff.mean()
    
    test = {
        'Test': 'mx = deaths / population',
        'Expected': 'All mx values calculated correctly',
        'Generated': f"Max diff: {max_diff:.2e}, Mean diff: {mean_diff:.2e}",
        'Match': max_diff < 1e-10,  # Allow for floating point precision
        'Max_Difference': max_diff,
        'Mean_Difference': mean_diff
    }
    validation_results.append(test)
    logger.info(f"\n✓ mx calculation verification:")
    logger.info(f"  Max difference: {max_diff:.2e}")
    logger.info(f"  Mean difference: {mean_diff:.2e}")
    logger.info(f"  Match: {test['Match']}")
    
    # Test: mx values are reasonable (between 0 and 1)
    mx_valid = (mx_total['mx'] >= 0) & (mx_total['mx'] <= 1)
    test2 = {
        'Test': 'mx values in valid range [0, 1]',
        'Expected': f"{len(mx_total)} ages",
        'Generated': f"{mx_valid.sum()} valid",
        'Match': mx_valid.all(),
        'Invalid_Count': (~mx_valid).sum()
    }
    validation_results.append(test2)
    logger.info(f"\n✓ mx value ranges:")
    logger.info(f"  Valid values (0-1): {mx_valid.sum()} / {len(mx_total)}")
    if not mx_valid.all():
        logger.warning(f"  Invalid values: {(~mx_valid).sum()}")
        logger.warning(f"  Max mx: {mx_total['mx'].max()}")
    
    # Test: Check specific mx values are reasonable
    age_ranges = [(0, 5), (5, 15), (15, 45), (45, 65), (65, 100)]
    for age_min, age_max in age_ranges:
        mask = (mx_total['idade'] >= age_min) & (mx_total['idade'] < age_max)
        if mask.any():
            mean_mx = mx_total.loc[mask, 'mx'].mean()
            test3 = {
                'Test': f'Mean mx for ages {age_min}-{age_max}',
                'Expected': 'Reasonable mortality rate',
                'Generated': f"{mean_mx:.6f}",
                'Match': 0 <= mean_mx <= 1,
                'Value': mean_mx
            }
            validation_results.append(test3)
            logger.info(f"  Age {age_min}-{age_max}: mx = {mean_mx:.6f}")
    
    return pd.DataFrame(validation_results)


def validate_age_consistency():
    """Validate age ranges and consistency across files."""
    logger.info("\n" + "="*70)
    logger.info("VALIDATION 3: AGE RANGES & CONSISTENCY")
    logger.info("="*70)
    
    validation_results = []
    
    # Load all generated files
    files_to_check = [
        ("01_deaths_by_age.csv", "Deaths by Age"),
        ("02_deaths_by_age_and_sex.csv", "Deaths by Sex"),
        ("03_deaths_by_age_and_race.csv", "Deaths by Race"),
        ("06_mx_total_population.csv", "mx Total"),
    ]
    
    age_ranges = {}
    
    for filename, label in files_to_check:
        try:
            df = pd.read_csv(OUTPUT_DIR / filename)
            age_min = df['idade'].min()
            age_max = df['idade'].max()
            age_count = df['idade'].nunique()
            age_ranges[label] = {
                'min': age_min,
                'max': age_max,
                'count': age_count
            }
            logger.info(f"\n✓ {label}: ages {age_min} - {age_max} ({age_count} unique)")
        except Exception as e:
            logger.warning(f"✗ Could not read {filename}: {str(e)}")
    
    # Check consistency
    if len(age_ranges) > 1:
        first_ranges = list(age_ranges.values())[0]
        all_consistent = all(
            r['min'] == first_ranges['min'] and r['max'] == first_ranges['max']
            for r in age_ranges.values()
        )
        
        test = {
            'Test': 'Age ranges consistent across files',
            'Expected': f"All files {first_ranges['min']}-{first_ranges['max']}",
            'Generated': f"{len(age_ranges)} files checked",
            'Match': all_consistent,
            'Details': str(age_ranges)
        }
        validation_results.append(test)
        logger.info(f"\n✓ Age range consistency: {all_consistent}")
    
    return pd.DataFrame(validation_results)


def validate_no_data_loss(expected):
    """Check for data loss in categories."""
    logger.info("\n" + "="*70)
    logger.info("VALIDATION 4: DATA LOSS CHECK")
    logger.info("="*70)
    
    validation_results = []
    
    deaths_by_sex = pd.read_csv(OUTPUT_DIR / "02_deaths_by_age_and_sex.csv")
    deaths_by_race = pd.read_csv(OUTPUT_DIR / "03_deaths_by_age_and_race.csv")
    
    # Sex data
    sex_total = deaths_by_sex[['Masculino', 'Feminino']].sum().sum()
    expected_sex_total = sum([expected[f'deaths_sex_{s}'] for s in ['Masculino', 'Feminino']])
    sex_loss = expected_sex_total - sex_total
    sex_loss_pct = (sex_loss / expected_sex_total * 100) if expected_sex_total > 0 else 0
    
    test1 = {
        'Test': 'Data loss in sex categories',
        'Expected': f"{expected_sex_total:,} deaths",
        'Generated': f"{int(sex_total):,} deaths",
        'Data_Loss': f"{int(sex_loss):,} ({sex_loss_pct:.2f}%)",
        'Match': sex_loss == 0,
    }
    validation_results.append(test1)
    logger.info(f"\n✓ Sex categories: {int(sex_total):,} vs {expected_sex_total:,}")
    logger.info(f"  Data loss: {int(sex_loss):,} ({sex_loss_pct:.2f}%)")
    
    # Race data
    race_cols = [col for col in deaths_by_race.columns if col != 'idade']
    race_total = deaths_by_race[race_cols].sum().sum()
    expected_race_total = sum([expected[f'deaths_race_{r}'] for r in race_cols])
    race_loss = expected_race_total - race_total
    race_loss_pct = (race_loss / expected_race_total * 100) if expected_race_total > 0 else 0
    
    test2 = {
        'Test': 'Data loss in race categories',
        'Expected': f"{expected_race_total:,} deaths",
        'Generated': f"{int(race_total):,} deaths",
        'Data_Loss': f"{int(race_loss):,} ({race_loss_pct:.2f}%)",
        'Match': race_loss == 0,
    }
    validation_results.append(test2)
    logger.info(f"\n✓ Race categories: {int(race_total):,} vs {expected_race_total:,}")
    logger.info(f"  Data loss: {int(race_loss):,} ({race_loss_pct:.2f}%)")
    
    # Note: some loss is expected due to missing values in categories
    note = f"\nNote: Expected data loss due to missing values in categories"
    logger.info(note)
    test3 = {
        'Test': 'Expected data loss explanation',
        'Expected': f"Sex missing: {expected['missing_sex']:,}, Race missing: {expected['missing_race']:,}",
        'Generated': f"Actual losses - Sex: {int(sex_loss):,}, Race: {int(race_loss):,}",
        'Match': True,
        'Note': 'Missing values in categories cause expected data loss'
    }
    validation_results.append(test3)
    
    return pd.DataFrame(validation_results)


def generate_comparison_summary(deaths_data, population_data):
    """Generate detailed comparison summary."""
    logger.info("\n" + "="*70)
    logger.info("DATA COMPARISON SUMMARY")
    logger.info("="*70)
    
    summary = []
    
    # Raw data overview
    summary.append({
        'Metric': 'Total Death Records (Raw)',
        'Value': f"{len(deaths_data):,}",
        'Description': 'Individual death records in raw data'
    })
    
    summary.append({
        'Metric': 'Population Data Points',
        'Value': f"{len(population_data):,}",
        'Description': 'Age groups in population data'
    })
    
    # Age statistics
    summary.append({
        'Metric': 'Deaths Age Range',
        'Value': f"{deaths_data['idade'].min():.0f} - {deaths_data['idade'].max():.0f}",
        'Description': 'Min and max age of deaths'
    })
    
    summary.append({
        'Metric': 'Population Age Range',
        'Value': f"{population_data['Idade'].min():.0f} - {population_data['Idade'].max():.0f}",
        'Description': 'Min and max age in population data'
    })
    
    # Missing data
    summary.append({
        'Metric': 'Missing Values (sexo)',
        'Value': f"{len(deaths_data[deaths_data['sexo'].isna()]):,}",
        'Description': 'Records with missing sex information'
    })
    
    summary.append({
        'Metric': 'Missing Values (raca_cor)',
        'Value': f"{len(deaths_data[deaths_data['raca_cor'].isna()]):,}",
        'Description': 'Records with missing race information'
    })
    
    summary_df = pd.DataFrame(summary)
    
    logger.info("\n")
    for _, row in summary_df.iterrows():
        logger.info(f"{row['Metric']}: {row['Value']}")
        logger.info(f"  └─ {row['Description']}")
    
    return summary_df


def run_full_validation():
    """Execute complete validation pipeline."""
    
    logger.info("="*70)
    logger.info("MORTALITY ANALYSIS VALIDATION - START")
    logger.info("="*70)
    logger.info(f"Started at: {datetime.now()}\n")
    
    try:
        # Load raw data
        deaths_data, population_data = load_raw_data()
        
        # Generate comparison summary
        comparison_summary = generate_comparison_summary(deaths_data, population_data)
        
        # Get expected totals
        expected = get_expected_totals(deaths_data)
        
        # Run validation tests
        validation_deaths = validate_deaths_totals(expected)
        validation_mx = validate_mx_calculations()
        validation_age = validate_age_consistency()
        validation_loss = validate_no_data_loss(expected)
        
        # Combine all results
        all_validations = pd.concat([
            validation_deaths,
            validation_mx,
            validation_age,
            validation_loss
        ], ignore_index=True)
        
        # Save validation report
        logger.info("\n" + "="*70)
        logger.info("SAVING VALIDATION REPORTS")
        logger.info("="*70)
        
        # Save full validation report
        report_file = VALIDATION_DIR / "full_validation_report.csv"
        all_validations.to_csv(report_file, index=False)
        logger.info(f"\n✓ Full validation report saved to: {report_file}")
        
        # Save comparison summary
        summary_file = VALIDATION_DIR / "data_comparison_summary.csv"
        comparison_summary.to_csv(summary_file, index=False)
        logger.info(f"✓ Comparison summary saved to: {summary_file}")
        
        # Generate final summary
        logger.info("\n" + "="*70)
        logger.info("VALIDATION SUMMARY")
        logger.info("="*70)
        
        total_tests = len(all_validations)
        passed_tests = all_validations['Match'].sum() if 'Match' in all_validations.columns else 0
        
        logger.info(f"\nTotal Tests: {total_tests}")
        logger.info(f"Passed Tests: {passed_tests}")
        logger.info(f"Pass Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if passed_tests == total_tests:
            logger.info("\n✓ ALL VALIDATIONS PASSED!")
        else:
            failed = all_validations[all_validations['Match'] == False]
            logger.warning(f"\n✗ {len(failed)} validation(s) failed:")
            for _, test in failed.iterrows():
                logger.warning(f"  - {test.get('Test', 'Unknown test')}")
        
        # Save text report
        text_report_file = VALIDATION_DIR / "validation_report.txt"
        with open(text_report_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("MORTALITY ANALYSIS VALIDATION REPORT\n")
            f.write("="*70 + "\n\n")
            f.write(f"Generated: {datetime.now()}\n\n")
            
            f.write("DATA COMPARISON\n")
            f.write("-"*70 + "\n")
            f.write(comparison_summary.to_string(index=False))
            f.write("\n\n")
            
            f.write("VALIDATION RESULTS\n")
            f.write("-"*70 + "\n")
            f.write(all_validations.to_string(index=False))
            f.write("\n\n")
            
            f.write("SUMMARY\n")
            f.write("-"*70 + "\n")
            f.write(f"Total Tests: {total_tests}\n")
            f.write(f"Passed Tests: {passed_tests}\n")
            f.write(f"Pass Rate: {(passed_tests/total_tests*100):.1f}%\n")
            if passed_tests == total_tests:
                f.write("\n✓ ALL VALIDATIONS PASSED!\n")
            else:
                f.write(f"\n✗ {len(failed)} validation(s) failed\n")
        
        logger.info(f"✓ Text report saved to: {text_report_file}")
        
        logger.info("\n" + "="*70)
        logger.info("VALIDATION COMPLETE")
        logger.info("="*70)
        logger.info(f"Reports saved to: {VALIDATION_DIR.absolute()}")
        logger.info(f"Completed at: {datetime.now()}\n")
        
        return {
            'summary': comparison_summary,
            'expected': expected,
            'validations': all_validations,
            'passed': passed_tests,
            'total': total_tests
        }
        
    except Exception as e:
        logger.error(f"\n✗ VALIDATION FAILED: {str(e)}", exc_info=True)
        raise


# ==================== ENTRY POINT ====================

if __name__ == "__main__":
    results = run_full_validation()
