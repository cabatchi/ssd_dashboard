SSD Test Dashboard

An interactive Streamlit dashboard for exploring SSD test results: test volume, failure rates by firmware version, daily failure trends, and read latency statistics by drive model.

Live version: https://ssd.cabatchi.dev


Note: All data in this project is synthetic. It was created to practice the kind of cleaning and analysis used on manufacturing test data. It does not come from any real company or product.

What it does
Filters by drive model and factory from the sidebar.
Summary metrics: total tests, failures, and overall failure rate for the current filter.
Failure rate by firmware version: bar chart plus a table of tests, failures, and failure rate per firmware version. Missing firmware versions are shown as "Unknown."
Daily failure rate: line chart of failure rate over time.
Read latency by model: mean, median, and standard deviation of read latency (microseconds) for each model.
Record viewers: expandable tables for the filtered and unfiltered data.
Data cleaning

The raw dataset (data/test_data.csv) contains deliberate quality problems. dataprep.py inspects and cleans it, then writes data/data_cleaned.csv.

Inspection reports:

row and column counts
duplicate records
missing values, overall and by column
minimum and maximum of each numeric column

Cleaning steps:

Strip extra whitespace from factory names, so the same factory is not counted as two.
Remove duplicate rows.
Drop rows missing a device_id or test_result, since they cannot be identified or scored.
Keep only rows whose test_result is PASS or FAIL.
Flag negative read latencies as invalid (invalid_read_latency).
Flag unusual read latencies per model using the 1.5 × IQR rule (unusual_read_latency).

Steps 5 and 6 flag rows rather than delete them, so the original values stay available for review.

Project structure
ssd_dashboard/
├── app.py            # Streamlit dashboard: filters, metrics, charts, tables
├── analysis.py       # Reusable summary functions: failure rates, latency stats, daily trend
├── dataprep.py       # Load, inspect, clean, and save the dataset
├── requirements.txt
└── data/
    ├── test_data.csv      # Raw synthetic data
    └── data_cleaned.csv   # Output of dataprep.py
Running locally

Requires Python 3.

bash
git clone https://github.com/cabatchi/ssd_dashboard.git
cd ssd_dashboard
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python dataprep.py               # regenerates data/data_cleaned.csv
streamlit run app.py

python analysis.py prints the summary tables to the terminal without starting the dashboard.

Built with

Python, pandas, Matplotlib, Streamlit

Planned improvements
Exclude flagged invalid latencies from the latency statistics, or show them separately.
Add charts for latency distribution by model.
Add curve fitting (SciPy) with goodness-of-fit metrics.
Pin package versions and add a Dockerfile.
