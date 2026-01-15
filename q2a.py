import streamlit as st

rules = [
    {
        "name": "Windows open → turn AC off",
        "priority": 100,
        "conditions": [
            ["windows_open", "==", True]
        ],
        "action": {
            "ac_mode": "OFF",
            "fan_speed": "LOW",
            "setpoint": None,
            "reason": "Windows are open"
        }
    },
    {
        "name": "No one home → eco mode",
        "priority": 90,
        "conditions": [
            ["occupancy", "==", "EMPTY"],
            ["temperature", ">=", 24]
        ],
        "action": {
            "ac_mode": "ECO",
            "fan_speed": "LOW",
            "setpoint": 27,
            "reason": "Home empty; save energy"
        }
    },
    {
        "name": "Hot & humid (occupied) → cool strong",
        "priority": 80,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["temperature", ">=", 30],
            ["humidity", ">=", 70]
        ],
        "action": {
            "ac_mode": "COOL",
            "fan_speed": "HIGH",
            "setpoint": 23,
            "reason": "Hot and humid"
        }
    },
    {
        "name": "Night (occupied) → sleep mode",
        "priority": 75,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["time_of_day", "==", "NIGHT"],
            ["temperature", ">=", 26]
        ],
        "action": {
            "ac_mode": "SLEEP",
            "fan_speed": "LOW",
            "setpoint": 26,
            "reason": "Night comfort"
        }
    },
    {
        "name": "Hot (occupied) → cool",
        "priority": 70,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["temperature", ">=", 28]
        ],
        "action": {
            "ac_mode": "COOL",
            "fan_speed": "MEDIUM",
            "setpoint": 24,
            "reason": "Temperature high"
        }
    },
    {
        "name": "Slightly warm (occupied) → gentle cool",
        "priority": 60,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["temperature", ">=", 26],
            ["temperature", "<", 28]
        ],
        "action": {
            "ac_mode": "COOL",
            "fan_speed": "LOW",
            "setpoint": 25,
            "reason": "Slightly warm"
        }
    },
    {
        "name": "Too cold → turn off",
        "priority": 85,
        "conditions": [
            ["temperature", "<=", 22]
        ],
        "action": {
            "ac_mode": "OFF",
            "fan_speed": "LOW",
            "setpoint": None,
            "reason": "Already cold"
        }
    }
]

def check_condition(facts, cond):
    """cond = [field, operator, value]"""
    field, op, value = cond
    left = facts[field]

    if op == "==":
        return left == value
    if op == ">=":
        return left >= value
    if op == "<=":
        return left <= value
    if op == ">":
        return left > value
    if op == "<":
        return left < value
    return False

def rule_matches(facts, rule):
    # all conditions must be true (AND)
    return all(check_condition(facts, c) for c in rule["conditions"])

def infer_engine(facts):
    matched = [r for r in rules if rule_matches(facts, r)]
    if not matched:
        return None, []
    matched.sort(key=lambda r: r["priority"], reverse=True)
    return matched[0], matched

# =========================
# STREAMLIT UI
# =========================
st.title("Question 2(a) - Rule-Based Smart AC Controller")

temperature = st.number_input("Temperature (°C)", value=22.0, step=0.5)
humidity = st.number_input("Humidity (%)", value=46.0, step=1.0)
occupancy = st.selectbox("Occupancy", ["OCCUPIED", "EMPTY"], index=0)
time_of_day = st.selectbox("Time of day", ["MORNING", "AFTERNOON", "EVENING", "NIGHT"], index=3)
windows_open = st.checkbox("Windows open?", value=False)

facts = {
    "temperature": float(temperature),
    "humidity": float(humidity),
    "occupancy": occupancy,
    "time_of_day": time_of_day,
    "windows_open": windows_open
}

if st.button("Get AC Decision"):
    best_rule, matched_rules = infer_engine(facts)

    st.subheader("Matched Rules")
    if matched_rules:
        for r in matched_rules:
            st.write(f"- {r['name']} (priority {r['priority']})")
    else:
        st.write("❌ No rules matched.")

    st.subheader("Final Decision (Highest Priority)")
    if best_rule:
        a = best_rule["action"]
        st.success(f"Rule chosen: {best_rule['name']} (priority {best_rule['priority']})")
        st.write("**AC Mode:**", a["ac_mode"])
        st.write("**Fan Speed:**", a["fan_speed"])
        st.write("**Setpoint:**", "-" if a["setpoint"] is None else f"{a['setpoint']}°C")
        st.write("**Reason:**", a["reason"])
    else:
        st.warning("No decision because no rule matched.")
