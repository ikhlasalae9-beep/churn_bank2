import joblib
import pandas as pd
import plotly.express as px
import streamlit as st

from .preprocessing import MODEL_FEATURE_COLUMNS, MODEL_PATH


@st.cache_resource
def load_model_for_info():
    return joblib.load(MODEL_PATH)


def render_model_info() -> None:
    st.title("Model Information")

    try:
        model = load_model_for_info()
    except Exception as exc:
        st.error(f"Unable to load model information: {exc}")
        return

    params = model.get_params()
    st.markdown(
        f"""
        ### Deployed Model
        The deployed estimator is a Random Forest classifier saved from the
        notebook as `random_forest_model.pkl`.

        ### Hyperparameters
        - `n_estimators`: {params.get("n_estimators")}
        - `criterion`: {params.get("criterion")}
        - `max_depth`: {params.get("max_depth")}
        - `max_features`: {params.get("max_features")}
        - `min_samples_split`: {params.get("min_samples_split")}
        - `min_samples_leaf`: {params.get("min_samples_leaf")}
        - `class_weight`: {params.get("class_weight")}
        - `random_state`: {params.get("random_state")}

        ### Feature Contract
        The model receives exactly {len(MODEL_FEATURE_COLUMNS)} ordered features
        after the notebook preprocessing and feature engineering pipeline.
        """
    )

    st.markdown("### Feature Importance")
    importance_df = pd.DataFrame(
        {
            "Feature": MODEL_FEATURE_COLUMNS,
            "Importance": model.feature_importances_,
        }
    ).sort_values("Importance", ascending=True)

    fig = px.bar(
        importance_df,
        x="Importance",
        y="Feature",
        orientation="h",
        template="plotly_dark",
        color_discrete_sequence=["#2f81f7"],
        text="Importance",
    )
    fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
    fig.update_layout(
        paper_bgcolor="#111318",
        plot_bgcolor="#1e222b",
        font={"color": "#f2f5f9"},
        height=620,
        margin=dict(l=20, r=55, t=30, b=45),
        xaxis=dict(gridcolor="#333947", linecolor="#465064", zerolinecolor="#465064"),
        yaxis=dict(gridcolor="#333947", linecolor="#465064", zerolinecolor="#465064"),
    )
    st.plotly_chart(fig, use_container_width=True)
