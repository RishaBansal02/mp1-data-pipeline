# MP1 Data Pipeline

This project loads tabular data and cleans it using settings in `config/config.yaml`. The root `pipeline.py` coordinates loading, validation, processing, reporting, and saving. The modules in `src/` divide the work: `data_loaders.py` reads input files, `data_validator.py` checks required columns and numeric values, and `data_processor.py` handles duplicates, missing values, and outliers. `data_output.py` saves the cleaned CSV, while `utils.py` configures logging and validates file paths. The `fixtures/` directory contains the sample input data, and generated files are saved in `output/`. With the provided sample data, validation reduced the row count from 100 to 98, and processing reduced it to 92.

## Run the pipeline

```bash
python pipeline.py --input fixtures/sample_data.csv --output output/clean.csv --config config/config.yaml --verbose
```

Example output:

```text
INFO src.data_loaders — Loaded CSV file: fixtures/sample_data.csv (100 rows)
INFO src.data_loaders — Loaded YAML file: config/config.yaml
WARNING src.data_validator — Removed 2 rows with invalid numeric values in rating
INFO __main__ — Validation complete: 100 -> 98 rows
INFO __main__ — Processing complete: 98 -> 92 rows
INFO __main__ — Saved cleaned data to output/clean.csv

Cleaning report:
{'rows_before': 98, 'rows_after': 92, 'rows_removed': 6, 'columns_before': 5, 'columns_after': 5, 'columns_removed': 0}
```