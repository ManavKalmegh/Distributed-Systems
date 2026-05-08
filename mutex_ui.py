import streamlit as st
import matplotlib.pyplot as plt
import math
import time

# =========================================================
# MAIN ENTRY
# =========================================================
def run_mutex_ui():
    st.title("🔐 Mutual Exclusion (Ricart–Agrawala)")
    auto_mutex_ui()


# =========================================================
# VISUALIZATION (WITH ARROWS)
# =========================================================
def draw_processes(processes):
    fig, ax = plt.subplots()

    n = len(processes)
    radius = 5

    for i, p in enumerate(processes.keys()):
        angle = 2 * math.pi * i / n
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)

        state = processes[p]["state"]

        if state == "HELD":
            color = "green"
        elif state == "WANTED":
            color = "orange"
        else:
            color = "lightgray"

        circle = plt.Circle((x, y), 0.8, color=color)
        ax.add_patch(circle)

        ax.text(x, y, p, ha='center', va='center', fontsize=12)

    ax.set_xlim(-7, 7)
    ax.set_ylim(-7, 7)
    ax.set_aspect('equal')
    ax.axis('off')

    st.pyplot(fig)

# =========================================================
# AUTO SIMULATION
# =========================================================
def auto_mutex_ui():

    # ===== SESSION STATE =====
    if "step_idx" not in st.session_state:
        st.session_state.step_idx = 0

    if "steps" not in st.session_state:
        st.session_state.steps = []

    if "play" not in st.session_state:
        st.session_state.play = False

    st.subheader("Auto Simulation (Timestamp-Based)")

    n = st.number_input("Number of Processes", min_value=1, step=1)

    request_times = {}
    for i in range(1, n + 1):
        request_times[f"P{i}"] = st.number_input(
            f"P{i} (0 = active, 1+ = request time)",
            min_value=0,
            value=0,
            key=f"p{i}"
        )

    # ===== VALIDATION =====
    if st.button("Run Simulation"):

        if all(t == 0 for t in request_times.values()):
            st.error("❌ No process is requesting the critical section.")
            return

        processes = {}
        time_groups = {}

        for p, t in request_times.items():
            processes[p] = {
                "time": t,
                "replies": set(),
                "deferred": set(),
                "active": True,
                "state": "RELEASED"
            }

            # Only add to request timeline if t > 0
            if t > 0:
                time_groups.setdefault(t, []).append(p)

        global_queue = []
        steps = []

        def snapshot(logs, time_val):
            state_copy = {
                p: {
                    "state": processes[p]["state"],
                    "replies": set(processes[p]["replies"]),
                    "deferred": set(processes[p]["deferred"])
                }
                for p in processes
            }

            steps.append({
                "time": time_val,
                "logs": logs.copy(),
                "state": state_copy,
            })

        max_time = max(time_groups.keys()) if time_groups else 0

        for current_time in range(0, max_time + 1):

            time_log = []

            if current_time not in time_groups:
                time_log.append("⚪ No events")
                snapshot(time_log, current_time)
                continue

            time_log.append(f"📌 Activated: {time_groups[current_time]}")

            # Activate
            for p in time_groups[current_time]:
                processes[p]["state"] = "WANTED"
                global_queue.append((current_time, p))

            global_queue.sort()

            # Requests
            for p in time_groups[current_time]:
                time_log.append(f"🔵 {p} sends REQUEST({current_time})")

            # Replies
            for p in time_groups[current_time]:
                for other in processes:
                    if other == p:
                        continue

                    if not processes[other]["active"]:
                        processes[p]["replies"].add(other)
                        time_log.append(f"{other} → {p} : REPLY (idle)")

                    elif processes[other]["state"] == "RELEASED":
                        processes[p]["replies"].add(other)
                        time_log.append(f"{other} → {p} : REPLY")

                    elif processes[other]["state"] == "HELD":
                        processes[other]["deferred"].add(p)
                        time_log.append(f"{other} defers reply to {p}")

                    elif processes[other]["state"] == "WANTED":
                        if (processes[other]["time"], other) < (current_time, p):
                            processes[other]["deferred"].add(p)
                            time_log.append(f"{other} defers reply to {p}")
                        else:
                            processes[p]["replies"].add(other)
                            time_log.append(f"{other} → {p} : REPLY")

            # CS Execution (FIXED 🔥)
            # ❌ Skip CS execution at time 0
            if current_time == 0:
                snapshot(time_log, current_time)
                continue

            while global_queue:
                t, p = global_queue[0]
                t, p = global_queue[0]

                if processes[p]["state"] != "WANTED":
                    global_queue.pop(0)
                    continue

                if len(processes[p]["replies"]) < n - 1:
                    break

                # ENTER
                processes[p]["state"] = "HELD"
                snapshot(time_log + [f"🟢 {p} ENTERS CS"], current_time)

                # EXIT
                processes[p]["state"] = "RELEASED"
                time_log.append(f"{p} EXITS CS")

                for d in processes[p]["deferred"]:
                    processes[d]["replies"].add(p)
                    time_log.append(f"{p} → {d} : REPLY (deferred)")

                processes[p]["deferred"].clear()
                processes[p]["replies"].clear()

                global_queue.pop(0)

            snapshot(time_log, current_time)

        st.session_state.steps = steps
        st.session_state.step_idx = 0

    # ===== DISPLAY =====
    if st.session_state.steps:

        steps = st.session_state.steps
        idx = min(st.session_state.step_idx, len(steps) - 1)
        step = steps[idx]

        col1, col2 = st.columns([2, 1])

        # LEFT
        with col1:
            draw_processes(step["state"])

            st.markdown("---")

            c1, c2, c3 = st.columns(3)

            with c1:
                if st.button("⬅️ Previous") and idx > 0:
                    st.session_state.step_idx -= 1

            with c2:
                if st.button("🔄 Reset"):
                    st.session_state.step_idx = 0

            with c3:
                if st.button("➡️ Next") and idx < len(steps) - 1:
                    st.session_state.step_idx += 1

            col_play, col_stop = st.columns(2)

            with col_play:
                if st.button("▶️ Play"):
                    st.session_state.play = True

            with col_stop:
                if st.button("⏹ Stop"):
                    st.session_state.play = False

        # RIGHT (SCROLLABLE 🔥)
        with col2:
            st.markdown("### 📜 Event Log")
            st.markdown(f"#### ⏱️ TIME = {step['time']}")

            log_html = "<div style='height:400px; overflow-y:auto;'>"
            for log in step["logs"]:
                log_html += f"<p>{log}</p>"
            log_html += "</div>"

            st.markdown(log_html, unsafe_allow_html=True)

            st.markdown(f"**Step {idx + 1} / {len(steps)}**")

        # AUTO PLAY
        if st.session_state.play:
            time.sleep(0.6)

            if st.session_state.step_idx < len(steps) - 1:
                st.session_state.step_idx += 1
                st.rerun()
            else:
                st.session_state.play = False

