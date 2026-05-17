import importlib
import subprocess
import sys
from pathlib import Path

import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

from styles import APP_CSS


def launch_with_streamlit_when_run_directly() -> None:
    if get_script_run_ctx() is not None:
        return

    app_path = Path(__file__).resolve()
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.address",
        "127.0.0.1",
        "--server.port",
        "8501",
    ]
    print("Starting Streamlit server at http://127.0.0.1:8501")
    subprocess.run(command, check=False)
    raise SystemExit


st.set_page_config(
    page_title="Bank Churn Prediction",
    layout="wide",
    initial_sidebar_state="expanded",
)


PAGES = {
    "Home": ("views.home", "render_home"),
    "Single Prediction": ("views.single_prediction", "render_single_prediction"),
    "Batch Prediction": ("views.batch_prediction", "render_batch_prediction"),
    "Prediction History": ("views.history", "render_history"),
    "Exploratory Data Analysis": ("views.eda", "render_eda"),
    "Model Performance": ("views.performance", "render_performance"),
    "Model Information": ("views.model_info", "render_model_info"),
}


def initialize_session_state() -> None:
    if "navigation_key" not in st.session_state:
        st.session_state["navigation_key"] = "Home"

    if "history" not in st.session_state:
        st.session_state.history = {"single": [], "batch": []}
    elif isinstance(st.session_state.history, list):
        st.session_state.history = {"single": st.session_state.history, "batch": []}

    if "prediction_history" in st.session_state and st.session_state.prediction_history:
        st.session_state.history["single"].extend(st.session_state.prediction_history)
        st.session_state.prediction_history = []


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown("### Enterprise Churn Intelligence")
        st.caption("Bank churn prediction platform")
        st.markdown("---")
        st.radio(
            "Navigation",
            list(PAGES.keys()),
            key="navigation_key",
            label_visibility="visible",
        )
        st.markdown("---")
        st.caption("Runtime theme: Dark")
        st.caption("Model family: Random Forest")
    return st.session_state["navigation_key"]


def render_page(selection: str) -> None:
    module_name, function_name = PAGES[selection]
    module = importlib.import_module(module_name)
    render_function = getattr(module, function_name)
    render_function()


def main() -> None:
    initialize_session_state()
    st.markdown(APP_CSS, unsafe_allow_html=True)
    selection = render_sidebar()
    render_page(selection)


if __name__ == "__main__":
    launch_with_streamlit_when_run_directly()
    main()
