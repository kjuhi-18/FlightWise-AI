import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu

from utils import (
    build_feature_vector,
    get_risk_level,
    get_recovery_actions
)

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="FlightWise",
    page_icon="✈️",
    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

.stMetric {
    border: 1px solid #333;
    padding: 15px;
    border-radius: 12px;
}

.block-container {
    padding-top: 1rem;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# LOAD FILES
# =====================================================

@st.cache_resource
def load_files():

    model = joblib.load(
        "models/flight_delay_model.pkl"
    )

    model_columns = joblib.load(
        "models/model_columns.pkl"
    )

    metrics = joblib.load(
        "models/metrics.pkl"
    )

    

    

 

    origin_traffic = joblib.load(
        "models/origin_traffic.pkl"
    )

    dest_traffic = joblib.load(
        "models/dest_traffic.pkl"
    )

    origin_freq = joblib.load(
        "models/origin_freq.pkl"
    )

    dest_freq = joblib.load(
        "models/dest_freq.pkl"
    )

    route_freq = joblib.load(
        "models/route_freq.pkl"
    )

    origin_state = joblib.load(
        "models/origin_state.pkl"
    )

    dest_state = joblib.load(
        "models/dest_state.pkl"
    )

    route_distance = joblib.load(
        "models/route_distance.pkl"
    )

    route_duration = joblib.load(
        "models/route_duration.pkl"
    )

    importance = pd.read_csv(
        "data/feature_importance.csv"
    )
    airline_routes = joblib.load(
    "models/airline_routes.pkl"
    )

    return (
        model,
        model_columns,
        metrics,
        origin_traffic,
        dest_traffic,
        origin_freq,
        dest_freq,
        route_freq,
        origin_state,
        dest_state,
        route_distance,
        route_duration,
        importance,
        airline_routes
    )

(
    model,
    model_columns,
    metrics,
    origin_traffic,
    dest_traffic,
    origin_freq,
    dest_freq,
    route_freq,
    origin_state,
    dest_state,
    route_distance,
    route_duration,
    importance,
    airline_routes
) = load_files()

# =====================================================
# HEADER
# =====================================================

st.title("✈️ FlightWise")
st.markdown("""
<div style="
padding:20px;
border-radius:15px;
background:linear-gradient(
90deg,
#0f172a,
#1e3a8a
);
">

<h2 style="color:white;">
AI-Powered Flight Delay Intelligence
</h2>

<p style="color:#d1d5db;">
Predict delays before they happen using
machine learning and aviation analytics.
</p>

</div>
""",
unsafe_allow_html=True)

st.markdown(
    "### AI-Powered Flight Delay Prediction & Recovery System"
)

# =====================================================
# NAVIGATION
# =====================================================

selected = option_menu(
    menu_title=None,
    options=[
        "Predictor",
        "Analytics",
        "Recovery Center",
        "About"
    ],
    icons=[
        "airplane",
        "bar-chart",
        "tools",
        "info-circle"
    ],
    orientation="horizontal"
)

# =====================================================
# PREDICTOR
# =====================================================

if selected == "Predictor":

    st.header("Flight Delay Predictor")

    col1, col2 = st.columns(2)

    with col1:

        airline = st.selectbox(
        "Operating Airline",
        sorted(airline_routes.keys())
        )

        available_origins = sorted(
        airline_routes[airline].keys()
        )

        origin = st.selectbox(
        "Origin Airport",
        available_origins
        )

        available_destinations = airline_routes[
            airline
        ][origin]

        destination = st.selectbox(
        "Destination Airport",
        available_destinations
    )

    with col2:

        flight_date = st.date_input(
            "Flight Date"
        )

        departure_time = st.time_input(
            "Departure Time"
        )

    if origin == destination:

        st.error(
            "Origin and Destination cannot be same."
        )

    else:

        route_key = (
        origin,
        destination
        )
        if route_key not in route_distance:

            st.error(
            "Route information unavailable."
            )

            st.stop()

        

        distance = route_distance.get(
            route_key,
            500
        )

        duration = route_duration.get(
            route_key,
            180
        )

        departure_hour = departure_time.hour

        arrival_hour = (
            departure_hour +
            int(duration // 60)
        ) % 24

        arrival_minute = departure_time.minute

        arrival_time_display = (
        f"{arrival_hour:02d}:{arrival_minute:02d}"
        )

        st.subheader(
    f"✈ {origin} → {destination}"
)

        k1, k2, k3 = st.columns(3)

        k1.metric(
         "Distance",
        f"{distance:.0f} mi"
        )

        k2.metric(
        "Duration",
        f"{duration:.0f} min"
        )

        k3.metric(
         "Arrival Time",
        arrival_time_display
        )
        if st.button(
            "🚀 Predict Delay Risk",
            use_container_width=True
        ):

            X = build_feature_vector(
                model_columns=model_columns,
                airline=airline,
                origin=origin,
                destination=destination,
                flight_date=flight_date,
                departure_hour=departure_hour,
                origin_traffic=origin_traffic,
                dest_traffic=dest_traffic,
                origin_freq=origin_freq,
                dest_freq=dest_freq,
                route_freq=route_freq,
                route_distance=route_distance,
                route_duration=route_duration,
                origin_state=origin_state,
                dest_state=dest_state
            )

            # If your utils returns tuple
            if isinstance(X, tuple):
                X = X[0]

            probability = model.predict_proba(X)[0][1]
            prediction = (
            "Delayed"
            if probability >= 0.35
            else "On Time"
            )
            

            risk = get_risk_level(
                probability
            )

            st.markdown("---")

            c1, c2 = st.columns([1, 1])

            with c1:

                fig = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=probability * 100,
                        title={
                            "text":
                            "Delay Probability (%)"
                        },
                        gauge={
                            "axis":{"range":[0,100]},
                            "steps":[
                                {"range":[0,30],"color":"green"},
                                {"range":[30,70],"color":"orange"},
                                {"range":[70,100],"color":"red"}
                            ]
                        }
                    )
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            with c2:
                if prediction == "Delayed":

                    st.error(
                        "✈️ DELAY EXPECTED"
                    )

                else:

                    st.success(
                        "✅ ON-TIME EXPECTED"
                    )
                st.metric(
                    "Delay Probability",
                    f"{probability*100:.2f}%"
                )

                if risk == "LOW":

                    st.success(
                        "🟢 LOW RISK"
                    )

                elif risk == "MEDIUM":

                    st.warning(
                        "🟠 MEDIUM RISK"
                    )

                else:

                    st.error(
                        "🔴 HIGH RISK"
                    )

                st.progress(
                    float(probability)
                )

# =====================================================
# ANALYTICS
# =====================================================

elif selected == "Analytics":

    st.header(
        "Model Performance Dashboard"
    )
    st.info("""
### Final Model

XGBoost Classifier

ROC-AUC : 0.78

Selected because it achieved the
best balance between recall,
precision and business usability.
""")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Accuracy",
        f"{metrics['Accuracy']:.2f}"
    )

    c2.metric(
        "Precision",
        f"{metrics['Precision']:.2f}"
    )

    c3.metric(
        "Recall",
        f"{metrics['Recall']:.2f}"
    )

    c4.metric(
        "F1",
        f"{metrics['F1']:.2f}"
    )

    c5.metric(
        "ROC-AUC",
        f"{metrics['ROC_AUC']:.2f}"
    )

    st.markdown("---")

    st.subheader(
        "Top Feature Importance"
    )

    top20 = (
    importance
    .sort_values(
        "Importance",
        ascending=False
    )
    .head(20)
)

    fig = px.bar(
        top20,
        x="Importance",
        y="Feature",
        orientation="h",
        color="Importance"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    st.dataframe(
    top20,
    use_container_width=True
)
    

# =====================================================
# RECOVERY CENTER
# =====================================================

elif selected == "Recovery Center":

    st.header(
        "Recovery Recommendation Engine"
    )

    probability = st.slider(
        "Delay Probability %",
        0,
        100,
        50
    ) / 100

    risk = get_risk_level(
        probability
    )

    actions = get_recovery_actions(
        probability
    )

    st.subheader(
        f"Risk Level: {risk}"
    )

    for action in actions:

        st.success(action)

# =====================================================
# ABOUT
# =====================================================

else:

    st.header("About FlightWise")

    st.markdown("""
### ✈️ FlightWise

AI-powered Flight Delay Prediction System built using:

- Python
- Streamlit
- XGBoost
- Plotly
- Machine Learning

### Dataset

- 558,715 flights
- BTS Aviation Dataset
- January 2024

### Models Evaluated

1. Logistic Regression
2. Random Forest
3. XGBoost

### Final Model

XGBoost

### Performance

- Accuracy: 80%
- Precision: 56%
- Recall: 50%
- F1 Score: 53%
- ROC-AUC: 78%

### Future Scope

- Real-time weather integration
- FAA API integration
- Airport congestion forecasting
- Delay recovery optimization
""")
    st.markdown("""
### Business Value

✔ Airport Operations

✔ Airline Scheduling

✔ Passenger Communication

✔ Delay Risk Monitoring

✔ Operational Recovery Planning
"""
                )
    st.info("""
👨‍💻 Built By

Kunal Jhindal

B.Tech AIML


""")
    st.markdown("---")

    st.caption(
    "FlightWise © 2026 | Built with Streamlit & XGBoost"
)