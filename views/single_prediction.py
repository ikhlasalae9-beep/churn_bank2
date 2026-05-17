from datetime import datetime

import joblib
import pandas as pd
import streamlit as st

from .preprocessing import MODEL_PATH, RAW_INPUT_COLUMNS, apply_notebook_preprocessing


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


def build_input_frame(values: dict) -> pd.DataFrame:
    return pd.DataFrame([{column: values[column] for column in RAW_INPUT_COLUMNS}])


def run_model_inference(model, input_frame: pd.DataFrame) -> tuple[int, float]:
    model_frame = apply_notebook_preprocessing(input_frame)
    prediction = int(model.predict(model_frame.to_numpy())[0])
    probability = float(model.predict_proba(model_frame.to_numpy())[0][1])
    return prediction, probability


def render_prediction_result(prediction: int, probability: float) -> None:
    if prediction == 1:
        label = "High Churn Risk"
        box_class = "danger"
        narrative = "The customer is classified as likely to churn."
    else:
        label = "Low Churn Risk"
        box_class = "success"
        narrative = "The customer is classified as likely to remain active."

    st.markdown(
        f"""
        <div class="status-box {box_class}">
            <h3>{label}</h3>
            <p>{narrative}</p>
            <p><strong>Estimated churn probability:</strong> {probability:.2%}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def append_history(values: dict, prediction: int, probability: float) -> None:
    if "history" not in st.session_state:
        st.session_state.history = {"single": [], "batch": []}
    st.session_state.history["single"].append(
        {
            "Type": "Single Customer Inference",
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "CreditScore": values["CreditScore"],
            "Geography": values["Geography"],
            "Gender": values["Gender"],
            "Age": values["Age"],
            "Tenure": values["Tenure"],
            "Balance": round(values["Balance"], 2),
            "NumOfProducts": values["NumOfProducts"],
            "HasCrCard": values["HasCrCard"],
            "IsActiveMember": values["IsActiveMember"],
            "EstimatedSalary": round(values["EstimatedSalary"], 2),
            "Prediction": "Churn" if prediction == 1 else "Retained",
            "ChurnProbability": f"{probability:.2%}",
        }
    )


def render_single_prediction() -> None:
    st.title("Single Customer Prediction")
    st.markdown(
        "Score an individual customer profile against the deployed Random Forest model."
    )

    try:
        model = load_model()
    except Exception as exc:
        st.error(f"Model loading failed: {exc}")
        return

    with st.form("single_prediction_form"):
        st.markdown("### Customer Attributes")
        col1, col2, col3 = st.columns(3)

        with col1:
            credit_score = st.number_input(
                "Credit Score", min_value=300, max_value=900, value=650, step=1
            )
            tenure = st.slider("Tenure", min_value=0, max_value=10, value=5)
            has_credit_card = st.selectbox("Has Credit Card", [1, 0])

        with col2:
            age = st.number_input("Age", min_value=18, max_value=100, value=38, step=1)
            balance = st.number_input(
                "Balance", min_value=0.0, value=75000.0, step=1000.0, format="%.2f"
            )
            is_active_member = st.selectbox("Is Active Member", [1, 0])

        with col3:
            geography = st.selectbox("Geography", ["France", "Germany", "Spain"])
            gender = st.selectbox("Gender", ["Male", "Female"])
            number_of_products = st.number_input(
                "Number of Products", min_value=1, max_value=4, value=2, step=1
            )
            estimated_salary = st.number_input(
                "Estimated Salary",
                min_value=0.0,
                value=100000.0,
                step=1000.0,
                format="%.2f",
            )

        submitted = st.form_submit_button("Run Prediction", use_container_width=True)

    if submitted:
        values = {
            "CreditScore": credit_score,
            "Geography": geography,
            "Gender": gender,
            "Age": age,
            "Tenure": tenure,
            "Balance": balance,
            "NumOfProducts": number_of_products,
            "HasCrCard": has_credit_card,
            "IsActiveMember": is_active_member,
            "EstimatedSalary": estimated_salary,
        }
        input_frame = build_input_frame(values)

        try:
            prediction, probability = run_model_inference(model, input_frame)
        except Exception as exc:
            st.error(f"Prediction failed. Verify the deployed model feature schema. Details: {exc}")
            return

        render_prediction_result(prediction, probability)
        append_history(values, prediction, probability)
