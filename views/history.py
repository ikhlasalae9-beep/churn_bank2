import pandas as pd
import streamlit as st


def get_history_store() -> dict:
    history = st.session_state.get("history", {"single": [], "batch": []})
    if isinstance(history, list):
        history = {"single": history, "batch": []}
    history.setdefault("single", [])
    history.setdefault("batch", [])
    st.session_state.history = history
    return history


def render_single_history(single_history: list[dict]) -> None:
    st.markdown("### Single Customer Inferences")
    if not single_history:
        st.info("No single-customer inferences have been recorded in this session.")
        return

    single_df = pd.DataFrame(single_history)
    ordered_columns = [
        "Timestamp",
        "CreditScore",
        "Geography",
        "Gender",
        "Age",
        "Tenure",
        "Balance",
        "NumOfProducts",
        "Prediction",
        "ChurnProbability",
    ]
    display_columns = [column for column in ordered_columns if column in single_df.columns]
    st.dataframe(single_df[display_columns], use_container_width=True, hide_index=True)


def render_batch_history(batch_history: list[dict]) -> None:
    st.markdown("### Batch Processing Logs")
    if not batch_history:
        st.info("No batch processing logs have been recorded in this session.")
        return

    batch_df = pd.DataFrame(batch_history)
    ordered_columns = [
        "Timestamp",
        "Filename",
        "Total Records Processed",
        "Churn Percentage",
    ]
    display_columns = [column for column in ordered_columns if column in batch_df.columns]
    st.dataframe(batch_df[display_columns], use_container_width=True, hide_index=True)


def render_history() -> None:
    st.title("Prediction History")
    st.markdown(
        "Review session-level single customer inferences and batch processing logs."
    )

    history = get_history_store()
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Single Inferences", len(history["single"]))
    with col2:
        st.metric("Batch Runs", len(history["batch"]))

    render_single_history(history["single"])
    render_batch_history(history["batch"])

    if history["single"] or history["batch"]:
        if st.button("Reset Session History", use_container_width=True):
            st.session_state.history = {"single": [], "batch": []}
            st.rerun()
