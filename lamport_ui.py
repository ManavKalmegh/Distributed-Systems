import streamlit as st
import matplotlib.pyplot as plt
from lamport import lamport_generate_steps


# ===== SIMPLE TIMELINE (STABLE) =====
def draw_lamport_timeline(steps, current_index):
    if not steps:
        return None

    fig, ax = plt.subplots(figsize=(8, 3))

    processes = list(steps[0]["clocks"].keys())
    y_positions = {p: i for i, p in enumerate(processes)}

    # Draw process lines
    for p in processes:
        ax.hlines(y_positions[p], 0, len(steps) + 1)
        ax.text(-0.5, y_positions[p], p, fontsize=10)

    message_positions = {}

    for t in range(current_index + 1):
        step = steps[t]
        text = step["text"]

        if "LOCAL" in text:
            p = text.split()[0]
            ax.plot(t + 1, y_positions[p], 'o')

        elif "SEND" in text:
            parts = text.split()
            sender = parts[0]
            msg = parts[2]

            ax.plot(t + 1, y_positions[sender], 'o')
            message_positions[msg] = (t + 1, sender)

        elif "RECEIVE" in text:
            parts = text.split()
            receiver = parts[0]
            msg = parts[2]

            ax.plot(t + 1, y_positions[receiver], 'o')

            if msg in message_positions:
                send_x, sender = message_positions[msg]

                ax.annotate(
                    "",
                    xy=(t + 1, y_positions[receiver]),
                    xytext=(send_x, y_positions[sender]),
                    arrowprops=dict(arrowstyle="->")
                )

    ax.set_xlim(0, len(steps) + 1)
    ax.set_ylim(-1, len(processes))
    ax.set_title("Lamport Timeline")
    ax.axis('off')

    return fig


# ===== MAIN UI =====
def run_lamport_ui():

    # st.set_page_config(page_title="Lamport Clock Simulation", layout="wide")
    st.title("🕒 Lamport Clock Simulation")

    # ===== INPUT =====
    n = st.number_input("Number of Processes", min_value=1, step=1)

    events_text = st.text_area(
        "Enter Events (one per line)",
        placeholder="local P1\nsend P1 P2 M1\nreceive P2 P1 M1"
    )

    # ===== SESSION STATE =====
    if "steps" not in st.session_state:
        st.session_state.steps = []
        st.session_state.index = 0
        st.session_state.event_log = []
        st.session_state.hb = []
        st.session_state.final_clocks = {}

    # ===== START =====
    if st.button("Start Simulation"):
        events = events_text.strip().split("\n")

        result = lamport_generate_steps(events, n)

        if len(result) == 2:
            steps, errors = result
            event_log, hb, final_clocks = [], [], {}
        else:
            steps, errors, event_log, hb, final_clocks = result

        if errors:
            st.error("⚠️ Errors in input:")
            for err in errors:
                st.write(err)
            st.session_state.steps = []
        else:
            st.session_state.steps = steps
            st.session_state.index = 0
            st.session_state.event_log = event_log
            st.session_state.hb = hb
            st.session_state.final_clocks = final_clocks

    # ===== DISPLAY =====
    if st.session_state.steps:

        step = st.session_state.steps[st.session_state.index]

        # ===== STEP =====
        st.subheader(f"Step {st.session_state.index}")
        st.success(step["text"])

        # ===== CLOCK VALUES =====
        st.write("### Clock Values")
        cols = st.columns(len(step["clocks"]))
        for i, (p, val) in enumerate(step["clocks"].items()):
            cols[i].metric(p, val)

        # ===== TIMELINE (KEY FIX: NO PLACEHOLDER) =====
        st.write("### Timeline Visualization")

        fig = draw_lamport_timeline(
            st.session_state.steps,
            st.session_state.index
        )

        if fig:
            st.pyplot(fig) 

        # ===== CONTROLS =====
        def next_step():
            if st.session_state.index < len(st.session_state.steps) - 1:
                st.session_state.index += 1

        def prev_step():
            if st.session_state.index > 0:
                st.session_state.index -= 1

        col1, col2 = st.columns(2)
        col1.button("⬅️ Previous", on_click=prev_step)
        col2.button("➡️ Next", on_click=next_step)

        # # ===== EVENT LOG =====
        # st.write("### 📜 Event Log (Till Now)")
        # if "event_log" in st.session_state and st.session_state.event_log:
        #     for i in range(st.session_state.index + 1):
        #         st.write(f"{i+1}. {st.session_state.event_log[i]}")
        # else:
        #     for i in range(st.session_state.index + 1):
        #         st.write(f"{i+1}. {st.session_state.steps[i]['text']}")

        # ===== FINAL SUMMARY =====
        st.write("---")
        st.write("## 📊 Final Summary")

        show_summary = (
            st.session_state.index == len(st.session_state.steps) - 1
            or st.button("Show Summary")
        )

        if show_summary:

            st.write("### --- Event History ---")
            for i, e in enumerate(st.session_state.event_log, 1):
                st.write(f"{i}. {e}")

            st.write("### --- Final Clock Values ---")
            last = st.session_state.final_clocks or st.session_state.steps[-1]["clocks"]

            cols = st.columns(len(last))
            for i, (p, val) in enumerate(last.items()):
                cols[i].metric(p, val)

            st.write("### --- Happens-Before Relationships ---")
            if st.session_state.hb:
                for hb in st.session_state.hb:
                    st.write(hb)
            else:
                st.write("None")

            st.success("System execution completed successfully.")