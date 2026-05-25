"""
Quick Validation Report - Mortality Analysis Data Integrity Check
==================================================================

Fast comparison of original data with generated results.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

DEATHS_DATA_PATH = "//Projetos2/Wrk/SIM-DATASUS/MICRODADOS/SIM-DATASUS-2020.csv"
POPULATION_DATA_PATH = "//Projetos2/Wrk/SIM-DATASUS/IBGE/censo2022.csv"
OUTPUT_DIR = Path("./output")
REPORT_DIR = Path("./validation_report")
REPORT_DIR.mkdir(exist_ok=True)

logger.info("="*80)
logger.info("MORTALITY ANALYSIS VALIDATION REPORT")
logger.info("="*80)

try:
    # ========== LOAD DATA ==========
    logger.info("\n[1/5] Loading data...")
    deaths = pd.read_csv(DEATHS_DATA_PATH)
    population = pd.read_csv(POPULATION_DATA_PATH)
    
    logger.info(f"  ✓ Deaths: {len(deaths):,} records")
    logger.info(f"  ✓ Population: {len(population):,} records")
    
    # ========== LOAD GENERATED FILES ==========
    logger.info("\n[2/5] Loading generated results...")
    deaths_by_age = pd.read_csv(OUTPUT_DIR / "01_deaths_by_age.csv")
    deaths_by_sex = pd.read_csv(OUTPUT_DIR / "02_deaths_by_age_and_sex.csv")
    deaths_by_race = pd.read_csv(OUTPUT_DIR / "03_deaths_by_age_and_race.csv")
    mx_total = pd.read_csv(OUTPUT_DIR / "06_mx_total_population.csv")
    
    logger.info("  ✓ All result files loaded")
    
    # ========== VALIDATION TESTS ==========
    logger.info("\n[3/5] Running validation tests...")
    
    results = []
    
    # Test 1: Total deaths
    raw_total = len(deaths)
    calc_total = deaths_by_age['deaths'].sum()
    
    results.append({
        'Test': 'Total Deaths Count',
        'Raw_Data': f"{raw_total:,}",
        'Generated': f"{int(calc_total):,}",
        'Status': '✓ PASS' if raw_total == calc_total else '✗ FAIL',
        'Difference': raw_total - int(calc_total)
    })
    logger.info(f"  Test 1: Total deaths - Raw: {raw_total:,} | Generated: {int(calc_total):,}")
    
    # Test 2: Deaths by sex
    male_raw = len(deaths[deaths['sexo'] == 1.0])
    female_raw = len(deaths[deaths['sexo'] == 2.0])
    male_gen = deaths_by_sex['Masculino'].sum()
    female_gen = deaths_by_sex['Feminino'].sum()
    
    results.append({
        'Test': 'Deaths by Sex - Masculino',
        'Raw_Data': f"{male_raw:,}",
        'Generated': f"{int(male_gen):,}",
        'Status': '✓ PASS' if male_raw == int(male_gen) else '✗ FAIL',
        'Difference': male_raw - int(male_gen)
    })
    
    results.append({
        'Test': 'Deaths by Sex - Feminino',
        'Raw_Data': f"{female_raw:,}",
        'Generated': f"{int(female_gen):,}",
        'Status': '✓ PASS' if female_raw == int(female_gen) else '✗ FAIL',
        'Difference': female_raw - int(female_gen)
    })
    logger.info(f"  Test 2: Sex - Masculino: {male_raw:,} | {int(male_gen):,}")
    logger.info(f"  Test 3: Sex - Feminino: {female_raw:,} | {int(female_gen):,}")
    
    # Test 3: Deaths by race
    race_labels = {'1': 'Branca', '2': 'Preta', '3': 'Amarela', '4': 'Parda', '5': 'Indígena'}
    for code, label in race_labels.items():
        race_raw = len(deaths[deaths['raca_cor'] == float(code)])
        if label in deaths_by_race.columns:
            race_gen = deaths_by_race[label].sum()
            results.append({
                'Test': f'Deaths by Race - {label}',
                'Raw_Data': f"{race_raw:,}",
                'Generated': f"{int(race_gen):,}",
                'Status': '✓ PASS' if race_raw == int(race_gen) else '✗ FAIL',
                'Difference': race_raw - int(race_gen)
            })
            logger.info(f"  Test: {label}: {race_raw:,} | {int(race_gen):,}")
    
    # Test 4: mx calculation verification
    mx_calc = mx_total['deaths'] / mx_total['population']
    mx_diff = (mx_calc - mx_total['mx']).abs().max()
    
    results.append({
        'Test': 'mx Calculation Accuracy',
        'Raw_Data': 'mx = deaths/population',
        'Generated': f'Max diff: {mx_diff:.2e}',
        'Status': '✓ PASS' if mx_diff < 1e-10 else '✗ FAIL',
        'Difference': mx_diff
    })
    logger.info(f"  Test: mx calculation - Max difference: {mx_diff:.2e}")
    
    # Test 5: mx value ranges
    mx_valid = ((mx_total['mx'] >= 0) & (mx_total['mx'] <= 1)).all()
    
    results.append({
        'Test': 'mx Value Range [0,1]',
        'Raw_Data': f'Range: 0-1',
        'Generated': f'Min: {mx_total["mx"].min():.6f}, Max: {mx_total["mx"].max():.6f}',
        'Status': '✓ PASS' if mx_valid else '✗ FAIL',
        'Difference': 0 if mx_valid else 1
    })
    logger.info(f"  Test: mx ranges - Min: {mx_total['mx'].min():.6f}, Max: {mx_total['mx'].max():.6f}")
    
    # Test 6: Age range consistency
    age_range_consistent = (
        deaths_by_age['idade'].min() == deaths_by_sex['idade'].min() ==
        deaths_by_race['idade'].min() == mx_total['idade'].min()
    ) and (
        deaths_by_age['idade'].max() == deaths_by_sex['idade'].max() ==
        deaths_by_race['idade'].max() == mx_total['idade'].max()
    )
    
    results.append({
        'Test': 'Age Range Consistency',
        'Raw_Data': f"{deaths['idade'].min():.0f}-{deaths['idade'].max():.0f}",
        'Generated': f"{deaths_by_age['idade'].min():.0f}-{deaths_by_age['idade'].max():.0f}",
        'Status': '✓ PASS' if age_range_consistent else '✗ FAIL',
        'Difference': 0 if age_range_consistent else 1
    })
    logger.info(f"  Test: Age ranges - All files consistent: {age_range_consistent}")
    
    # ========== SAVE RESULTS ==========
    logger.info("\n[4/5] Saving validation results...")
    
    results_df = pd.DataFrame(results)
    report_file = REPORT_DIR / "quick_validation_report.csv"
    results_df.to_csv(report_file, index=False)
    logger.info(f"  ✓ Report saved: {report_file}")
    
    # ========== GENERATE TEXT REPORT ==========
    text_file = REPORT_DIR / "VALIDATION_SUMMARY.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("MORTALITY ANALYSIS VALIDATION REPORT\n")
        f.write("="*80 + "\n\n")
        
        f.write("RAW DATA SUMMARY\n")
        f.write("-"*80 + "\n")
        f.write(f"Total death records: {len(deaths):,}\n")
        f.write(f"Population records: {len(population):,}\n")
        f.write(f"Age range (deaths): {deaths['idade'].min():.0f} - {deaths['idade'].max():.0f}\n")
        f.write(f"Age range (population): {population['Idade'].min():.0f} - {population['Idade'].max():.0f}\n\n")
        
        f.write("GENERATED DATA SUMMARY\n")
        f.write("-"*80 + "\n")
        f.write(f"Deaths aggregated: {deaths_by_age['deaths'].sum():,.0f}\n")
        f.write(f"Age groups processed: {len(deaths_by_age)}\n")
        f.write(f"Sex categories: {', '.join([c for c in deaths_by_sex.columns if c != 'idade'])}\n")
        f.write(f"Race categories: {', '.join([c for c in deaths_by_race.columns if c != 'idade'])}\n")
        f.write(f"mx values calculated: {len(mx_total)}\n\n")
        
        f.write("VALIDATION RESULTS\n")
        f.write("-"*80 + "\n")
        f.write(results_df.to_string(index=False))
        f.write("\n\n")
        
        pass_count = (results_df['Status'] == '✓ PASS').sum()
        total_tests = len(results_df)
        f.write("SUMMARY\n")
        f.write("-"*80 + "\n")
        f.write(f"Tests Passed: {pass_count}/{total_tests}\n")
        f.write(f"Success Rate: {(pass_count/total_tests*100):.1f}%\n\n")
        
        if pass_count == total_tests:
            f.write("✓ ALL VALIDATIONS PASSED - Data integrity verified!\n")
        else:
            failed = results_df[results_df['Status'] == '✗ FAIL']
            f.write(f"✗ {len(failed)} validation(s) failed - Review required\n\n")
            for _, test in failed.iterrows():
                f.write(f"  FAILED: {test['Test']}\n")
                f.write(f"    Raw: {test['Raw_Data']} | Generated: {test['Generated']}\n")
    
    logger.info(f"  ✓ Summary saved: {text_file}")
    
    # ========== DISPLAY SUMMARY ==========
    logger.info("\n[5/5] VALIDATION SUMMARY")
    logger.info("-"*80)
    
    pass_count = (results_df['Status'] == '✓ PASS').sum()
    total_tests = len(results_df)
    
    logger.info(f"\nTests Passed: {pass_count}/{total_tests}")
    logger.info(f"Success Rate: {(pass_count/total_tests*100):.1f}%\n")
    
    if pass_count == total_tests:
        logger.info("✓✓✓ ALL VALIDATIONS PASSED! ✓✓✓")
        logger.info("Data integrity verified - Results are ready for visualization!")
    else:
        logger.info("✗ Some validations failed - Review the report")
        failed = results_df[results_df['Status'] == '✗ FAIL']
        for _, test in failed.iterrows():
            logger.info(f"  FAILED: {test['Test']}")
    
    logger.info("\n" + "="*80)
    logger.info(f"Reports saved to: {REPORT_DIR.absolute()}\n")

except Exception as e:
    logger.error(f"\n✗ VALIDATION ERROR: {str(e)}\n", exc_info=True)
    raise
