from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
RAW_PATH = DATA_DIR / "test_data.csv"
CLEAN_PATH = DATA_DIR / "data_cleaned.csv"

DATA_DIR.mkdir(exist_ok = True)


def data_load() -> pd.DataFrame:
    
    # LOAD DATAFRAME, PARSE TIME/DATE
    df = pd.read_csv(RAW_PATH, parse_dates=["test_timestamp"],)

    # RETURN DATAFRAME
    return df


def data_inspect(df: pd.DataFrame) -> None:
    # REPORT ROW COUNT
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    
    # FIND DUPLICATES
    dupes = df[df.duplicated()]

    # AGGREGATE VALUES
    numeric_values = df.select_dtypes(include = "number")
    ranges = numeric_values.agg(["min", "max"]).T

    # FIND MISSING VALUES
    missing_cells = df.isna().sum().sum() 
    
    missing_rows = df.isna().any(axis = 1).sum()
    
    missing_by_column = df.isna().sum()
    columns_with_missing = missing_by_column[missing_by_column > 0]

    # GENERATE DATA REPORT
    print(f"{len(dupes)} duplicate records")
    print(f"{missing_cells} missing cells")
    print(f"{missing_rows} rows have missing values")

    print("Columns with missing values and quantity: ")
    print(columns_with_missing.to_string())

    print("\nNumeric ranges:")
    print(ranges)



def data_clean(df: pd.DataFrame) -> pd.DataFrame:
    # COPY THE DATA TO TEMP
    cleaned = df.copy()
    cleaned["factory"] = cleaned["factory"].str.strip()

    # REMOVE DUPE ROWS
    cleaned = cleaned.drop_duplicates()

    # REMOVE UNIDENTIFIABLE ENTRIES
    cleaned = cleaned.dropna(subset = ["device_id", "test_result"])

    # FLAG ALL VALUES THAT ARE VALID FOR TEST RESULTS
    valid_result = cleaned["test_result"].isin(["PASS", "FAIL"])
    # ONLY INCLUDE VALID VALUES IN NEW DATAFRAME
    cleaned = cleaned[valid_result].copy()

    # FLAG NEGATIVE LATENCIES WITH NEW COLUMN
    cleaned["invalid_read_latency"] = (cleaned["read_latency_us"].notna() & (cleaned["read_latency_us"] < 0))

    # FIND OUTLIERS BY MODEL
    grouped = cleaned.groupby("model")["read_latency_us"]
    q1 = grouped.transform(lambda values: values.quantile(0.25))
    q3 = grouped.transform(lambda values: values.quantile(0.75))
    iqr = q3 - q1

    # CHECK FOR ROWS ABOVE/BELOW LIMIT
    cleaned["unusual_read_latency"] = (iqr > 0) & ((cleaned["read_latency_us"] < q1 - 1.5 * iqr) | (cleaned["read_latency_us"] > q3 + 1.5 * iqr)) 

    return cleaned
    

def data_clean_save(df: pd.DataFrame) -> None:
    # SAVE CLEANED DATA TO ITS OWN FILE
    df.to_csv(CLEAN_PATH, index=False)
    print(f"\nSaved cleaned data to: {CLEAN_PATH}")

def main() -> None:
    df = data_load()

    print("RAW DATA REPORT")
    data_inspect(df)

    cleaned = data_clean(df)

    print("\nCLEANING REPORT")
    print(f"Rows retained: {len(cleaned)}")
    print(f"Rows removed: {len(df) - len(cleaned)}")
    print(
        "Negative read latencies:",
        cleaned["invalid_read_latency"].sum(),
    )
    print(
        "Unusual read latencies:",
        cleaned["unusual_read_latency"].sum(),
    )

    data_clean_save(cleaned)
    # LOAD -> INSPECT -> CLEAN -> REPORT -> SAVE

if __name__ == "__main__":
    main()