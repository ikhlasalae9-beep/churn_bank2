from io import BytesIO
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from fpdf import FPDF

from .preprocessing import RAW_INPUT_COLUMNS, apply_notebook_preprocessing
from .single_prediction import load_model


def validate_batch_schema(df: pd.DataFrame) -> list[str]:
    required_columns = [
        column for column in RAW_INPUT_COLUMNS if column not in ["Geography", "Gender"]
    ]
    return [column for column in required_columns if column not in df.columns]


def predict_batch(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        raise ValueError("The uploaded CSV does not contain any rows.")

    missing = validate_batch_schema(df)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    model = load_model()
    result = df.copy()
    features = result.copy()
    if "Geography" not in features:
        features["Geography"] = "France"
    if "Gender" not in features:
        features["Gender"] = "Male"

    processed_features = apply_notebook_preprocessing(features[RAW_INPUT_COLUMNS])
    feature_matrix = processed_features.to_numpy()
    predictions = model.predict(feature_matrix)
    probabilities = model.predict_proba(feature_matrix)[:, 1]

    result["Prediction"] = pd.Series(predictions).map({0: "Retained", 1: "Churn"})
    result["ChurnProbability"] = probabilities.round(4)
    return result


def apply_chart_layout(fig: go.Figure, height: int = 390) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#111318",
        plot_bgcolor="#1e222b",
        font={"color": "#f2f5f9"},
        height=height,
        margin=dict(l=20, r=20, t=55, b=45),
    )
    fig.update_xaxes(gridcolor="#333947", linecolor="#465064", zerolinecolor="#465064")
    fig.update_yaxes(gridcolor="#333947", linecolor="#465064", zerolinecolor="#465064")
    return fig


def prediction_pie_chart(df: pd.DataFrame) -> go.Figure:
    counts = df["Prediction"].value_counts().reset_index()
    counts.columns = ["Prediction", "Count"]
    fig = px.pie(
        counts,
        names="Prediction",
        values="Count",
        color="Prediction",
        color_discrete_map={"Retained": "#8b949e", "Churn": "#2f81f7"},
        template="plotly_dark",
        hole=0.42,
    )
    fig.update_layout(title="Predicted Churn Mix")
    return apply_chart_layout(fig)


def geography_bar_chart(df: pd.DataFrame) -> go.Figure:
    chart_df = df.copy()
    if "Geography" not in chart_df:
        chart_df["Geography"] = "Unspecified"
    distribution = (
        chart_df.groupby(["Geography", "Prediction"], as_index=False)
        .size()
        .rename(columns={"size": "Count"})
    )
    fig = px.bar(
        distribution,
        x="Geography",
        y="Count",
        color="Prediction",
        barmode="group",
        template="plotly_dark",
        color_discrete_map={"Retained": "#8b949e", "Churn": "#2f81f7"},
    )
    fig.update_layout(title="Prediction Distribution by Geography")
    return apply_chart_layout(fig)


def build_excel_payload(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Predictions")
        summary = (
            df["Prediction"]
            .value_counts()
            .rename_axis("Prediction")
            .reset_index(name="Count")
        )
        summary.to_excel(writer, index=False, sheet_name="Summary")
    return output.getvalue()


def build_pdf_payload(df: pd.DataFrame) -> bytes:
    total_records = len(df)
    churn_count = int((df["Prediction"] == "Churn").sum())
    retained_count = total_records - churn_count
    churn_rate = churn_count / total_records if total_records else 0
    average_probability = df["ChurnProbability"].mean() if total_records else 0

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Bank Churn Batch Prediction Report", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Total records processed: {total_records:,}", ln=True)
    pdf.cell(0, 8, f"Predicted churn records: {churn_count:,}", ln=True)
    pdf.cell(0, 8, f"Predicted retained records: {retained_count:,}", ln=True)
    pdf.cell(0, 8, f"Predicted churn rate: {churn_rate:.2%}", ln=True)
    pdf.cell(0, 8, f"Average churn probability: {average_probability:.2%}", ln=True)
    pdf.ln(6)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Operational Summary", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(
        0,
        7,
        "The batch dataset was scored with vectorized preprocessing and "
        "Random Forest inference. Use the exported prediction table for "
        "retention prioritization and downstream reporting.",
    )
    payload = pdf.output(dest="S")
    if isinstance(payload, str):
        return payload.encode("latin-1")
    return bytes(payload)


def render_export_options(processed_df: pd.DataFrame) -> None:
    st.markdown("### Export Options")
    csv_payload = processed_df.to_csv(index=False).encode("utf-8")
    excel_payload = build_excel_payload(processed_df)
    pdf_payload = build_pdf_payload(processed_df)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "Download CSV",
            data=csv_payload,
            file_name="bank_churn_predictions.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col2:
        st.download_button(
            "Download Excel",
            data=excel_payload,
            file_name="bank_churn_predictions.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with col3:
        st.download_button(
            "Download PDF Report",
            data=pdf_payload,
            file_name="bank_churn_batch_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


def append_batch_history(filename: str, processed_df: pd.DataFrame) -> None:
    if "history" not in st.session_state:
        st.session_state.history = {"single": [], "batch": []}
    total_records = len(processed_df)
    churn_percentage = (
        (processed_df["Prediction"].eq("Churn").sum() / total_records) if total_records else 0
    )
    st.session_state.history["batch"].append(
        {
            "Type": "Batch Processing Log",
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Filename": filename,
            "Total Records Processed": total_records,
            "Churn Percentage": f"{churn_percentage:.2%}",
        }
    )


def render_batch_prediction() -> None:
    st.title("Batch CSV Prediction")
    st.markdown(
        "Upload a CSV file and score all records using vectorized Random Forest inference."
    )

    uploaded_file = st.file_uploader("CSV input file", type=["csv"])
    if uploaded_file is None:
        st.markdown(
            """
            <div class="app-card">
                <strong>Required schema for model inference</strong>
                <p class="muted">
                    CreditScore, Age, Tenure, Balance, NumOfProducts, HasCrCard,
                    IsActiveMember, EstimatedSalary. Geography and Gender are
                    supported when present and defaulted when absent.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    try:
        raw_df = pd.read_csv(uploaded_file)
    except Exception as exc:
        st.error(f"CSV parsing failed: {exc}")
        return

    st.markdown("### Raw Data Preview")
    st.dataframe(raw_df.head(20), use_container_width=True)

    missing_columns = validate_batch_schema(raw_df)
    if missing_columns:
        st.error(f"Missing required columns: {', '.join(missing_columns)}")
        return

    if st.button("Process Batch Dataset", use_container_width=True):
        try:
            with st.spinner("Processing batch dataset..."):
                processed_df = predict_batch(raw_df)
                append_batch_history(uploaded_file.name, processed_df)
        except Exception as exc:
            st.error(f"Batch prediction failed: {exc}")
            return

        st.markdown(
            f"""
            <div class="status-box success">
                <h3>Batch Processing Complete</h3>
                <p>{len(processed_df):,} records were scored successfully.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### Processed Results")
        st.dataframe(processed_df, use_container_width=True)

        st.markdown("### Results Visualization")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(prediction_pie_chart(processed_df), use_container_width=True)
        with col2:
            st.plotly_chart(geography_bar_chart(processed_df), use_container_width=True)

        render_export_options(processed_df)
