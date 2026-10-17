from pathlib import Path
import pandas as pd

def metrics(df: pd.DataFrame) -> dict:
    test_count = len(df)
    failure_count = int(df["test_result"].eq("FAIL").sum())

    failure_rate = (failure_count / test_count * 100 if test_count > 0 else None)

    return{
        "tests": test_count,
        "failures": failure_count,
        "failure_rate": failure_rate,
        "median_read_latency_us": df["read_latency_us"].median(),}

def failure_summary(df: pd.DataFrame, group_column: str) -> pd.DataFrame:
    results = []

    # CREATE GROUPS FOR ANALYSIS

    groups = df.groupby(group_column, dropna = False)

    for group_name, records in groups:
        tests_total = len(records)
        tests_failed = len(records[records["test_result"] == "FAIL"])
        test_failure_rate = (tests_failed / tests_total) * 100

        results.append({
            group_column: group_name,
            "tests": tests_total,
            "failures": tests_failed,
            "failure_rate": test_failure_rate
        })
    
    columns = [group_column, "tests", "failures", "failure_rate"]
    return pd.DataFrame(results, columns = columns)

def performance_summary(df: pd.DataFrame, group_column: str, measurement: str = "read_latency_us") -> pd.DataFrame:
    results = []
    groups = df.groupby(group_column, dropna = False)

    for group_name, records in groups:
        values = records[measurement].dropna()

        results.append({
            group_column: group_name,
            "measurements": len(values),
            "mean": values.mean(),
            "median": values.median(),
            "std": values.std()
        })

    columns = [group_column, "measurements", "mean", "median", "std"]
    return pd.DataFrame(results, columns = columns)

def daily_trend(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()

    # STRIP TIME OFF OF ENTRIES
    working["test_date"] = working["test_timestamp"].dt.date

    return failure_summary(working, "test_date")

if __name__ == "__main__":
    path = Path(__file__).parent / "data" / "data_cleaned.csv"
    df = pd.read_csv(path, parse_dates = ["test_timestamp"])

    print(metrics(df))
    print(failure_summary(df, "firmware_version").to_string(index = False))
    print(performance_summary(df, "model").to_string(index = False))
    print(daily_trend(df).to_string(index = False))