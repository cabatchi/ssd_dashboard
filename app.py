from pathlib import Path
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from analysis import metrics, failure_summary, performance_summary, daily_trend

CLEAN_PATH = Path(__file__).parent / "data" / "data_cleaned.csv"

def main():
    st.set_page_config(page_title = "SSD Test Dashboard", layout = "wide")
    st.title("SSD Test Dashboard")
    st.caption("Synthetic SSD test data generated using ChatGPT")

    df = pd.read_csv(CLEAN_PATH, parse_dates = ["test_timestamp"])

    # DROPDOWN?
    models = ["All"] + sorted(df["model"].dropna().unique().tolist())
    factories = ["All"] + sorted(df["factory"].dropna().unique().tolist())

    selected_model = st.sidebar.selectbox("Model", models)
    selected_factory = st.sidebar.selectbox("Factory", factories)

    filtered = df.copy()

    if selected_model != "All":
        filtered = filtered[filtered["model"] == selected_model]

    if selected_factory != "All":
        filtered = filtered[filtered["factory"] == selected_factory]

    if filtered.empty:
        st.info("No records match these filters.")
        st.stop()

    # CALCULATIONS
    summary = metrics(filtered)
    failure_rate = summary["failures"] / summary["tests"] * 100

    col1, col2, col3 = st.columns(3)
    
    col1.metric("Tests", f"{summary['tests']:,}")
    col2.metric("Failures", f"{summary['failures']:,}")
    col3.metric("Failure rate", f"{failure_rate:.2f}%")

    # FAILURE RATES
    st.subheader("Failure rate by firmware")

    firmware = failure_summary(filtered, "firmware_version")
    firmware["firmware_version"] = (firmware["firmware_version"].fillna("Unknown"))

    fig, ax = plt.subplots(figsize = (8, 4))
    ax.bar(
        firmware["firmware_version"],
        firmware["failure_rate"],
        color="#36586b",
    )
    ax.set_xlabel("Firmware version")
    ax.set_ylabel("Failure rate (%)")
    ax.set_ylim(bottom=0)

    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.dataframe(firmware, hide_index=True)

    # DAILY FAILURES
    st.subheader("Daily failure rate")

    daily = daily_trend(filtered).sort_values("test_date")

    fig, ax = plt.subplots(figsize = (10, 4))
    ax.plot(daily["test_date"], daily["failure_rate"], color = "#36586b")
    ax.set_xlabel("Test date")
    ax.set_ylabel("Failure rate (%)")
    ax.set_ylim(bottom = 0)

    fig.autofmt_xdate()
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # Display latency statistics.
    st.subheader("Read latency by model (microseconds)")
    performance = performance_summary(filtered, "model")
    st.dataframe(performance, hide_index = True)

    # Let users inspect the records behind the summaries.
    with st.expander("View filtered records"):
        st.dataframe(filtered, hide_index = True)


if __name__ == "__main__":
    main()
