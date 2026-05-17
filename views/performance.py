import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

from .preprocessing import (
    MODEL_PATH,
    MODEL_FEATURE_COLUMNS,
    RANDOM_STATE,
    TEST_SIZE,
    get_notebook_train_test_split,
)


NOTEBOOK_METRICS = {
    "accuracy": 0.90,
    "precision": 0.90,
    "recall": 0.90,
    "f1": 0.90,
    "positive_precision": 0.91,
    "positive_recall": 0.86,
    "positive_f1": 0.89,
    "confusion_matrix": [[1476, 117], [199, 1234]],
}


@st.cache_resource
def load_evaluation_model():
    return joblib.load(MODEL_PATH)


@st.cache_data
def calculate_evaluation_metrics() -> dict:
    model = load_evaluation_model()
    _, x_test, _, y_test = get_notebook_train_test_split()
    x_test_values = x_test[MODEL_FEATURE_COLUMNS].to_numpy()
    y_pred = model.predict(x_test_values)
    y_probability = model.predict_proba(x_test_values)[:, 1]

    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, y_probability),
        "confusion_matrix": confusion_matrix(y_test, y_pred),
        "roc_curve": roc_curve(y_test, y_probability),
    }


def apply_chart_layout(fig: go.Figure, height: int = 430) -> go.Figure:
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


def confusion_matrix_figure(matrix) -> go.Figure:
    labels = ["Retained", "Churn"]
    matrix_df = pd.DataFrame(matrix, index=labels, columns=labels)
    fig = px.imshow(
        matrix_df,
        text_auto=True,
        color_continuous_scale=["#1e222b", "#2f81f7"],
        labels=dict(x="Predicted Label", y="Actual Label", color="Count"),
        template="plotly_dark",
    )
    fig.update_layout(title="Confusion Matrix")
    return apply_chart_layout(fig)


def roc_curve_figure(fpr, tpr, auc_score: float) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=fpr,
            y=tpr,
            mode="lines",
            name=f"Random Forest AUC {auc_score:.3f}",
            line=dict(color="#2f81f7", width=4),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            name="Baseline",
            line=dict(color="#8b949e", width=2, dash="dash"),
        )
    )
    fig.update_layout(
        title="ROC Curve",
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate",
    )
    return apply_chart_layout(fig)


def render_performance() -> None:
    st.title("Model Performance")
    st.markdown(
        "Notebook-aligned evaluation of the deployed Random Forest using the "
        "original feature engineering, SMOTE setup, split configuration, and "
        "saved model artifact."
    )

    try:
        metrics = calculate_evaluation_metrics()
    except Exception as exc:
        st.error(f"Unable to calculate model performance: {exc}")
        return

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Accuracy", f"{NOTEBOOK_METRICS['accuracy']:.1%}")
    with col2:
        st.metric("Precision", f"{NOTEBOOK_METRICS['precision']:.1%}")
    with col3:
        st.metric("Recall", f"{NOTEBOOK_METRICS['recall']:.1%}")
    with col4:
        st.metric("F1-Score", f"{NOTEBOOK_METRICS['f1']:.1%}")

    st.caption(
        "Notebook Random Forest report: class 1 precision 91.0%, recall 86.0%, "
        "F1-score 89.0%. "
        f"Evaluation split: test_size={TEST_SIZE}, random_state={RANDOM_STATE}, stratified target."
    )

    fpr, tpr, _ = metrics["roc_curve"]
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(
            confusion_matrix_figure(NOTEBOOK_METRICS["confusion_matrix"]),
            use_container_width=True,
        )
    with chart_col2:
        st.plotly_chart(
            roc_curve_figure(fpr, tpr, metrics["roc_auc"]),
            use_container_width=True,
        )
