from pathlib import Path
from functools import lru_cache

import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


APP_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = APP_ROOT / "Churn_Modelling.csv"
MODEL_PATH = APP_ROOT / "random_forest_model.pkl"
TARGET_COLUMN = "Exited"
TEST_SIZE = 0.2
RANDOM_STATE = 42
SMOTE_SAMPLING_STRATEGY = 0.90
SMOTE_K_NEIGHBORS = 5
BASE_SCALED_COLUMNS = ["CreditScore", "Balance", "EstimatedSalary"]

RAW_INPUT_COLUMNS = [
    "CreditScore",
    "Geography",
    "Gender",
    "Age",
    "Tenure",
    "Balance",
    "NumOfProducts",
    "HasCrCard",
    "IsActiveMember",
    "EstimatedSalary",
]

MODEL_FEATURE_COLUMNS = [
    "CreditScore",
    "Age",
    "Tenure",
    "Balance",
    "NumOfProducts",
    "HasCrCard",
    "IsActiveMember",
    "EstimatedSalary",
    "Geography_Germany",
    "Geography_Spain",
    "Gender_Male",
    "BalanceSalaryRatio",
    "TenureByAge",
    "AgeScore",
    "CreditScoreByAge",
    "IsSenior",
    "HasBalance",
    "ActiveWithCard",
    "Balance_per_Tenure",
    "Balance_to_Salary",
    "Age_per_Tenure",
]


def load_churn_dataset() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def normalize_raw_input(df: pd.DataFrame) -> pd.DataFrame:
    prepared = df.copy()
    if "Geography" not in prepared:
        prepared["Geography"] = "France"
    if "Gender" not in prepared:
        prepared["Gender"] = "Male"

    for column in [
        "CreditScore",
        "Age",
        "Tenure",
        "Balance",
        "NumOfProducts",
        "HasCrCard",
        "IsActiveMember",
        "EstimatedSalary",
    ]:
        prepared[column] = pd.to_numeric(prepared[column], errors="coerce")

    prepared["Geography"] = prepared["Geography"].astype(str)
    prepared["Gender"] = prepared["Gender"].astype(str)
    return prepared[RAW_INPUT_COLUMNS]


def _engineer_model_features(df: pd.DataFrame, base_scaler: StandardScaler) -> pd.DataFrame:
    prepared = normalize_raw_input(df)
    prepared[BASE_SCALED_COLUMNS] = base_scaler.transform(prepared[BASE_SCALED_COLUMNS])
    model_frame = pd.DataFrame(index=prepared.index)
    model_frame["CreditScore"] = prepared["CreditScore"].astype(float)
    model_frame["Age"] = prepared["Age"].astype(float)
    model_frame["Tenure"] = prepared["Tenure"].astype(float)
    model_frame["Balance"] = prepared["Balance"].astype(float)
    model_frame["NumOfProducts"] = prepared["NumOfProducts"].astype(float)
    model_frame["HasCrCard"] = prepared["HasCrCard"].astype(float)
    model_frame["IsActiveMember"] = prepared["IsActiveMember"].astype(float)
    model_frame["EstimatedSalary"] = prepared["EstimatedSalary"].astype(float)
    model_frame["Geography_Germany"] = (
        prepared["Geography"].str.strip().eq("Germany")
    ).astype(float)
    model_frame["Geography_Spain"] = (
        prepared["Geography"].str.strip().eq("Spain")
    ).astype(float)
    model_frame["Gender_Male"] = prepared["Gender"].str.strip().eq("Male").astype(float)
    model_frame["BalanceSalaryRatio"] = model_frame["Balance"] / (
        model_frame["EstimatedSalary"] + 1
    )
    model_frame["TenureByAge"] = model_frame["Tenure"] / (model_frame["Age"] + 1)
    model_frame["AgeScore"] = model_frame["Age"] * model_frame["NumOfProducts"]
    model_frame["CreditScoreByAge"] = model_frame["CreditScore"] / (
        model_frame["Age"] + 1
    )
    model_frame["IsSenior"] = (model_frame["Age"] >= 45).astype(float)
    model_frame["HasBalance"] = (model_frame["Balance"] > 0).astype(float)
    model_frame["ActiveWithCard"] = (
        model_frame["IsActiveMember"] * model_frame["HasCrCard"]
    )
    model_frame["Balance_per_Tenure"] = model_frame["Balance"] / (
        model_frame["Tenure"] + 1
    )
    model_frame["Balance_to_Salary"] = model_frame["Balance"] / (
        model_frame["EstimatedSalary"] + 1
    )
    model_frame["Age_per_Tenure"] = model_frame["Age"] / (model_frame["Tenure"] + 1)
    return model_frame[MODEL_FEATURE_COLUMNS].fillna(0).astype(float)


@lru_cache(maxsize=1)
def fit_notebook_preprocessors():
    raw_df = load_churn_dataset()
    base_scaler = StandardScaler()
    base_scaler.fit(raw_df[BASE_SCALED_COLUMNS])
    raw_features = _engineer_model_features(raw_df, base_scaler)
    target = raw_df[TARGET_COLUMN].astype(int)

    smote = SMOTE(
        sampling_strategy=SMOTE_SAMPLING_STRATEGY,
        k_neighbors=SMOTE_K_NEIGHBORS,
        random_state=RANDOM_STATE,
    )
    balanced_features, balanced_target = smote.fit_resample(raw_features, target)
    x_train, x_test, y_train, y_test = train_test_split(
        balanced_features,
        balanced_target,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=balanced_target,
    )
    final_scaler = StandardScaler()
    final_scaler.fit(x_train)
    return base_scaler, final_scaler, x_train, x_test, y_train, y_test


def apply_notebook_preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    base_scaler, final_scaler, *_ = fit_notebook_preprocessors()
    raw_features = _engineer_model_features(df, base_scaler)
    scaled_values = final_scaler.transform(raw_features[MODEL_FEATURE_COLUMNS])
    return pd.DataFrame(scaled_values, columns=MODEL_FEATURE_COLUMNS, index=df.index)


def prepare_training_data() -> tuple[pd.DataFrame, pd.Series]:
    _, _, x_train, _, y_train, _ = fit_notebook_preprocessors()
    _, final_scaler, *_ = fit_notebook_preprocessors()
    scaled_train = pd.DataFrame(
        final_scaler.transform(x_train),
        columns=MODEL_FEATURE_COLUMNS,
        index=x_train.index,
    )
    target = pd.Series(y_train).astype(int)
    target.index = scaled_train.index
    return scaled_train, target


def get_notebook_train_test_split():
    _, final_scaler, x_train, x_test, y_train, y_test = fit_notebook_preprocessors()
    scaled_train = pd.DataFrame(
        final_scaler.transform(x_train),
        columns=MODEL_FEATURE_COLUMNS,
        index=x_train.index,
    )
    scaled_test = pd.DataFrame(
        final_scaler.transform(x_test),
        columns=MODEL_FEATURE_COLUMNS,
        index=x_test.index,
    )
    y_train = pd.Series(y_train).astype(int)
    y_test = pd.Series(y_test).astype(int)
    y_train.index = scaled_train.index
    y_test.index = scaled_test.index
    return scaled_train, scaled_test, y_train, y_test
