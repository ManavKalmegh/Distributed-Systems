import streamlit as st

# Import UI functions (you will create these)
from lamport_ui import run_lamport_ui
from mutex_ui import run_mutex_ui
from deadlock_ui import run_deadlock_ui


st.set_page_config(page_title="Distributed Systems Simulator")

st.title("🧠 Distributed Systems Simulator")

st.write("Choose an algorithm to simulate:")

option = st.selectbox(
    "Select Module",
    ["Lamport Clock", "Mutual Exclusion", "Deadlock Detection"]
)

# ===== ROUTING =====

if option == "Lamport Clock":
    run_lamport_ui()

elif option == "Mutual Exclusion":
    run_mutex_ui()

elif option == "Deadlock Detection":
    run_deadlock_ui()