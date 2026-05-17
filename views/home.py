import joblib
import streamlit as st

from .preprocessing import DATA_PATH, MODEL_PATH, load_churn_dataset


def switch_page(page_name: str) -> None:
    st.session_state["navigation_key"] = page_name


def render_home() -> None:
    try:
        df = load_churn_dataset()
        model = joblib.load(MODEL_PATH)
    except Exception as exc:
        st.error(f"Application assets could not be loaded: {exc}")
        return

    st.markdown(
        """
        <div class="home-hero">
            <div class="hero-eyebrow">Enterprise Bank Churn Intelligence</div>
            <h1>Customer retention analytics powered by Random Forest inference.</h1>
            <p>
                Score individual customers, process batch portfolios, review model
                performance, and explore churn drivers through a unified dark-mode
                analytical workspace.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    action_col1, action_col2, spacer = st.columns([1.1, 1.1, 2.2])
    with action_col1:
        st.button(
            "Launch Single Prediction",
            use_container_width=True,
            on_click=switch_page,
            args=("Single Prediction",),
        )
    with action_col2:
        st.button(
            "Process Batch Dataset",
            use_container_width=True,
            on_click=switch_page,
            args=("Batch Prediction",),
        )

    st.markdown("### Technical Portfolio Snapshot")
    churn_rate = df["Exited"].mean()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Customers", f"{len(df):,}")
    with col2:
        st.metric("Observed Churn Rate", f"{churn_rate:.2%}")
    with col3:
        st.metric("Model Type", model.__class__.__name__)
    with col4:
        st.metric("Model Features", getattr(model, "n_features_in_", "N/A"))

    st.markdown(
        f"""
        <div class="app-card">
            <strong>Runtime Assets</strong>
            <p class="muted">Dataset: {DATA_PATH.name}</p>
            <p class="muted">Model: {MODEL_PATH.name}</p>
            <p class="muted">
                Prediction inputs are transformed into the exact feature sequence
                used during notebook training before inference is executed.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
