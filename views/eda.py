import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

from .preprocessing import load_churn_dataset


GOLD = "#dcbd92"
GOLD_BRIGHT = "#f8bb38"
PANEL = "#1e222b"
BACKGROUND = "#111318"
TEXT = "#f2f5f9"
MUTED = "#a9b2c3"
BLUE = "#2f81f7"
GRAY = "#8b949e"


def section_header(title: str) -> None:
    st.markdown(
        f"""
        <div class="eda-header">
            <h2>{title}</h2>
            <div class="accent-line"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def notebook_card(content: str) -> None:
    st.markdown(
        f"""
        <div class="app-card">
            {content}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_feature_engineering_optimization_section() -> None:
    section_header("Feature Engineering and Optimization")
    st.markdown(
        """
        This section summarizes the technical improvements that moved the project
        from a distance-based baseline to a stronger Random Forest classifier.
        The objective was to reduce bias, improve feature representation, and
        capture non-linear churn behavior more effectively.
        """
    )

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.metric("KNN Accuracy", "86.0%")
    with metric_col2:
        st.metric("Random Forest Accuracy", "90.0%")
    with metric_col3:
        st.metric("Performance Gain", "+4.0 pts")

    st.markdown(
        """
        <div class="app-card">
            <h3>1. Handling Class Imbalance: SMOTE Optimization</h3>
            <p class="muted">
                The original dataset was highly imbalanced: approximately 80% of
                customers stayed while only 20% exited. This imbalance can make
                classifiers biased toward the majority class and reduce churn
                detection quality.
            </p>
            <p class="muted">
                To address this, the training data was balanced with
                <code>SMOTE</code> using <code>sampling_strategy=0.90</code>.
                Synthetic minority samples were generated only on the training
                data, improving the model's exposure to churn patterns.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div class="app-card">
                <h3>2. Categorical Encoding: One-Hot Encoding</h3>
                <p class="muted">
                    The categorical columns <code>Geography</code> and
                    <code>Gender</code> were transformed using
                    <code>OneHotEncoder(drop='first')</code>.
                </p>
                <p class="muted">
                    This converted text categories into numeric dummy variables
                    while avoiding the dummy variable trap, keeping the feature
                    matrix compact and statistically stable.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="app-card">
                <h3>3. Feature Scaling: StandardScaler</h3>
                <p class="muted">
                    <code>StandardScaler</code> was applied to the continuous
                    numerical columns <code>CreditScore</code>,
                    <code>Balance</code>, and <code>EstimatedSalary</code>.
                </p>
                <p class="muted">
                    Scaling brought the numerical variables to comparable ranges,
                    supporting fair feature representation and improving stability
                    for models that are sensitive to magnitude differences.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="app-card">
            <h3>4. Random Forest configuration </h3>
            <p class="muted">
                The selected Random Forest configuration was:
                <code>n_estimators=180</code>, <code>criterion='entropy'</code>,
                and <code>max_depth=24</code>. This configuration improved the
                model's capacity to learn segmented churn patterns while limiting
                uncontrolled overfitting.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "Technical outcome: the optimized preprocessing and Random Forest "
        "ensemble improved model accuracy from 86.0% with KNN to 90.0% with "
        "Random Forest."
    )


def style_axis(ax, title: str | None = None) -> None:
    ax.set_facecolor(PANEL)
    ax.figure.set_facecolor(BACKGROUND)
    ax.tick_params(colors=MUTED)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    if title:
        ax.set_title(title, color=TEXT, fontweight="bold", pad=12)
    else:
        ax.title.set_color(TEXT)
    for spine in ax.spines.values():
        spine.set_color("#333947")
    ax.grid(axis="y", color="#333947", alpha=0.35)


def render_countplot(
    df,
    x: str,
    title: str,
    hue: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
) -> None:
    fig, ax = plt.subplots(figsize=(7, 4.4))
    palette = [GRAY, BLUE] if hue else [BLUE]
    sns.countplot(x=x, hue=hue, data=df, ax=ax, palette=palette)
    style_axis(ax, title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if ax.get_legend() is not None:
        ax.legend(facecolor=PANEL, edgecolor="#333947", labelcolor=TEXT, title=hue)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def render_kdeplot(df, x: str, title: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.kdeplot(
        data=df,
        x=x,
        hue="Exited",
        fill=True,
        common_norm=False,
        alpha=0.35,
        palette=[GRAY, BLUE],
        ax=ax,
    )
    style_axis(ax, title)
    if ax.get_legend() is not None:
        ax.legend(facecolor=PANEL, edgecolor="#333947", labelcolor=TEXT, title="Exited")
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def render_eda() -> None:
    st.title("Exploratory Data Analysis")
    st.markdown(
        "Professional Streamlit integration of the notebook EDA section, preserving "
        "the original order, graph types, variables, titles, and interpretations."
    )

    try:
        df = load_churn_dataset()
    except Exception as exc:
        st.error(f"Unable to load Churn_Modelling.csv: {exc}")
        return

    
    st.markdown(
        """
        ###  Analyse des variables catégorielles

        Nous analysons :
        - Gender vs Exited
        - Geography vs Exited

        Cela permet de voir si certaines catégories sont plus susceptibles de quitter.

        ---

        ###  Corrélation entre les variables

        Nous utilisons une matrice de corrélation pour identifier les relations entre variables numériques.

        ---

        ### Conclusion de l’analyse

        - La variable cible est déséquilibrée
        - L’âge influence fortement le churn
        - Les clients en Allemagne quittent plus
        - Les clients inactifs sont plus susceptibles de partir

        Ces observations guideront les étapes suivantes (cleaning et preprocessing).
        """
    )

    st.markdown("### 1. Analyse de la variable cible")
    st.markdown(
        """
        Nous commençons par analyser la distribution de la variable cible `Exited`.

        Cela permet de vérifier si les classes sont équilibrées ou non.
        """
    )
    render_countplot(
        df,
        x="Exited",
        title="Distribution de la variable cible (Exited)",
        xlabel="Exited (0 = Resté, 1 = Parti)",
        ylabel="Nombre de clients",
    )

    st.markdown("### 2. Relation entre les variables et le churn")
    st.markdown(
        """
        Nous analysons l’impact de certaines variables sur le churn :

        - Gender vs Exited
        - Geography vs Exited
        - NumOfProducts vs Exited

        Cela permet d’identifier les facteurs influençant le départ des clients.
        """
    )

    st.markdown("#### – Les hommes quittent-ils plus la banque que les femmes (ou inversement) ?")
    render_countplot(df, x="Gender", hue="Exited", title="Gender vs Churn (Exited)")
    st.markdown("*Le genre a un impact léger sur le churn, avec une tendance légèrement plus élevée chez les femmes*")

    st.markdown("#### – Quel pays a le taux de churn le plus élevé ?")
    render_countplot(df, x="Geography", hue="Exited", title="Geography vs Churn (Exited)")
    st.markdown("*La geographie a une impact léger sur le churn, avec une tendance chez 'France'*")

    st.markdown("#### – Est-ce que le nombre de produits influence le churn (Exited)")
    render_countplot(df, x="NumOfProducts", hue="Exited", title="NumOfProducts vs Churn (Exited)")
    st.markdown("*Le nombre de produits influence légerement sur le churn*")

    st.markdown("#### Notebook preview: `df.head(2)`")
    st.dataframe(df.head(2), use_container_width=True, hide_index=True)

    st.markdown("### 3. Distribution de churn selon:")
    st.markdown(
        """
        Nous analysons l’impact de certaines variables sur le churn :

        - Credit Score
        - Balance
        - Estimated Salary

        Cela permet d’identifier les facteurs influençant le départ des clients.
        """
    )

    st.markdown("#### – Credit Score")
    render_kdeplot(df, x="CreditScore", title="Credit Score vs Churn")
    st.markdown("*Le Credit Score peut influencer légèrement le churn*")

    st.markdown("#### – Balance")
    render_kdeplot(df, x="Balance", title="Credit Score vs Churn")
    st.markdown("*- Le Balance semble avoir une relation plus visible avec le départ des clients*")

    st.markdown("#### – Estimated Salary")
    render_kdeplot(df, x="EstimatedSalary", title="Credit Score vs Churn")

    section_header("Feature Engineering Connection")
    notebook_card(
        """
        <p class="muted">
            The notebook connects the EDA observations to the following engineered variables:
        </p>
        <ul>
            <li><code>BalanceSalaryRatio</code> = Balance / (EstimatedSalary + 1)</li>
            <li><code>TenureByAge</code> = Tenure / (Age + 1)</li>
            <li><code>AgeScore</code> = Age * NumOfProducts</li>
            <li><code>CreditScoreByAge</code> = CreditScore / (Age + 1)</li>
            <li><code>IsSenior</code> = Age >= 45</li>
            <li><code>HasBalance</code> = Balance > 0</li>
            <li><code>ActiveWithCard</code> = IsActiveMember * HasCrCard</li>
            <li><code>Balance_per_Tenure</code> = Balance / (Tenure + 1)</li>
            <li><code>Balance_to_Salary</code> = Balance / (EstimatedSalary + 1)</li>
            <li><code>Age_per_Tenure</code> = Age / (Tenure + 1)</li>
        </ul>
        <p class="muted">
            1. Tnasob d l-flous: Wach l-client 3ando crédit m9arnat b l-flous li 7at f l-banka?
        </p>
        <p class="muted">
            2. Interaction d l-3mer m3a les produits: Les clients li kbar f l-3mer o 3andhom bzaf d les produits homa li kay-churnew bzaf
        </p>
        <p class="muted">
            3. Score d l-fidélité sghira: L-3mer m3a tenure
        </p>
        """
    )

    render_feature_engineering_optimization_section()
