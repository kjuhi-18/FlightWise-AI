import pandas as pd
import numpy as np


# =====================================================
# TIME BLOCK
# =====================================================

def get_time_block(hour):
    """
    Convert hour to BTS time block

    Example:
    14 -> 1400-1459
    """

    start = f"{hour:02d}00"
    end = f"{hour:02d}59"

    return f"{start}-{end}"


# =====================================================
# DURATION CATEGORY
# =====================================================

def get_duration_category(duration):

    if duration <= 120:
        return "Short"

    elif duration <= 240:
        return "Medium"

    elif duration <= 360:
        return "Long"

    else:
        return "VeryLong"


# =====================================================
# WEEKEND FLAG
# =====================================================

def get_is_weekend(day_of_week):

    return int(day_of_week in [6, 7])


# =====================================================
# RISK LEVEL
# =====================================================

def get_risk_level(probability):

    if probability < 0.30:
        return "LOW"

    elif probability < 0.70:
        return "MEDIUM"

    else:
        return "HIGH"


# =====================================================
# RECOVERY ACTIONS
# =====================================================

def get_recovery_actions(probability):

    if probability < 0.30:

        return [
            "Flight expected to operate normally",
            "Routine monitoring only",
            "No operational intervention required"
        ]

    elif probability < 0.70:

        return [
            "Monitor flight status closely",
            "Alert operations team",
            "Track gate availability",
            "Keep passengers informed"
        ]

    else:

        return [
            "Notify passengers proactively",
            "Prepare alternate gate",
            "Arrange standby crew",
            "Monitor connecting passengers",
            "Coordinate with airport operations",
            "Prepare recovery schedule"
        ]


# =====================================================
# FEATURE VECTOR CREATION
# =====================================================

def build_feature_vector(
    model_columns,
    airline,
    origin,
    destination,
    flight_date,
    departure_hour,
    origin_traffic,
    dest_traffic,
    origin_freq,
    dest_freq,
    route_freq,
    route_distance,
    route_duration,
    origin_state,
    dest_state
):

    # =================================================
    # EMPTY DATAFRAME
    # =================================================

    X = pd.DataFrame(
        np.zeros((1, len(model_columns))),
        columns=model_columns
    )

    # =================================================
    # DATE FEATURES
    # =================================================

    day_of_month = flight_date.day

    day_of_week = flight_date.weekday() + 1

    X["DayofMonth"] = day_of_month

    X["DayOfWeek"] = day_of_week

    # =================================================
    # ROUTE FEATURES
    # =================================================

    route_key = (origin, destination)
    distance = route_distance.get(route_key, 500)
    duration = route_duration.get(route_key, 180)

    arrival_hour = (
        departure_hour +
        int(duration // 60)
    ) % 24

    X["Distance"] = distance

    X["DepartureHour"] = departure_hour

    X["ArrivalHour"] = arrival_hour

    X["IsWeekend"] = get_is_weekend(
        day_of_week
    )

    # =================================================
    # TRAFFIC FEATURES
    # =================================================

    X["OriginTraffic"] = (
        origin_traffic.get(origin, 0)
    )

    X["DestTraffic"] = (
        dest_traffic.get(destination, 0)
    )

    X["Origin_Freq"] = (
        origin_freq.get(origin, 0)
    )

    X["Dest_Freq"] = (
        dest_freq.get(destination, 0)
    )

    route_name = f"{origin}_{destination}"

    X["Route_Freq"] = (
        route_freq.get(route_name, 0)
    )

    # =================================================
    # AIRLINE FEATURES
    # =================================================

    airline_col = (
        f"Operating_Airline _{airline}"
    )

    if airline_col in X.columns:

        X.loc[0, airline_col] = 1

    # =================================================
    # MARKETING AIRLINE
    # =================================================

    marketing_col = (
        f"Marketing_Airline_Network_{airline}"
    )

    if marketing_col in X.columns:

        X.loc[0, marketing_col] = 1

    # =================================================
    # CODE SHARE
    # =================================================

    partner_col = (
        f"Operated_or_Branded_Code_Share_Partners_{airline}"
    )

    if partner_col in X.columns:

        X.loc[0, partner_col] = 1

    # =================================================
    # ORIGIN STATE
    # =================================================

    origin_state_name = (
        origin_state.get(origin)
    )

    if origin_state_name:

        state_col = (
            f"OriginStateName_{origin_state_name}"
        )

        if state_col in X.columns:

            X.loc[0, state_col] = 1

    # =================================================
    # DEST STATE
    # =================================================

    dest_state_name = (
        dest_state.get(destination)
    )

    if dest_state_name:

        state_col = (
            f"DestStateName_{dest_state_name}"
        )

        if state_col in X.columns:

            X.loc[0, state_col] = 1

    # =================================================
    # DEP TIME BLOCK
    # =================================================

    dep_block = (
        f"DepTimeBlk_{get_time_block(departure_hour)}"
    )

    if dep_block in X.columns:

        X.loc[0, dep_block] = 1

    # =================================================
    # ARR TIME BLOCK
    # =================================================

    arr_block = (
        f"ArrTimeBlk_{get_time_block(arrival_hour)}"
    )

    if arr_block in X.columns:

        X.loc[0, arr_block] = 1

    # =================================================
    # FLIGHT DURATION CATEGORY
    # =================================================

    duration_category = (
        get_duration_category(duration)
    )

    duration_col = (
        f"FlightDurationCategory_{duration_category}"
    )

    if duration_col in X.columns:

        X.loc[0, duration_col] = 1

    # =================================================
    # SAFETY CHECK
    # =================================================

    X = X.reindex(
        columns=model_columns,
        fill_value=0
    )

    return X, distance, duration, arrival_hour
