def handle_mutex():
    print("\n===== Mutual Exclusion (Ricart–Agrawala) =====\n")
    print("Choose mode:")
    print("\t1. Auto Simulation")
    print("\t2. Manual Simulation\n")

    choice = input("Enter choice: ").strip()

    if choice == "1":
        auto_mutex()
    elif choice == "2":
        manual_mutex()
    else:
        print("❌ Invalid choice\n")


def auto_mutex():
    try:
        n = int(input("\nEnter number of processes: "))
    except:
        print("Invalid input\n")
        return

    processes = {}
    time_groups = {}

    print("\nEnter request times:")

    # ===== INPUT HANDLING (FIXED) =====
    for i in range(1, n+1):
        p = f"P{i}"
        t = int(input(f"{p}: "))

        if t == -1:
            processes[p] = {
                "time": float('inf'),
                "replies": set(),
                "deferred": set(),
                "active": False
            }
        else:
            processes[p] = {
                "time": t,
                "replies": set(),
                "deferred": set(),
                "active": True
            }

            if t not in time_groups:
                time_groups[t] = []
            time_groups[t].append(p)

    state = {p: "RELEASED" for p in processes}
    global_queue = []
    timeline = []

    print("\n===== SIMULATION START =====")

    for current_time in sorted(time_groups.keys()):

        print(f"\n==============================")
        print(f"⏱️ TIME = {current_time}")
        print(f"==============================")

        # ===== ACTIVATE PROCESSES =====
        for p in sorted(time_groups[current_time]):
            if processes[p]["active"]:
                state[p] = "WANTED"
                global_queue.append((current_time, p))

        global_queue.sort()

        active_now = time_groups[current_time]
        print("\n📌 Activated Processes:", active_now)

        inactive = [p for p in processes if not processes[p]["active"]]
        if inactive:
            print("⚪ Idle (never request):", inactive)

        print("🔎 States (after activation):", state)

        # ===== SEND REQUESTS =====
        for p in time_groups[current_time]:
            print(f"\n🔵 {p} sends REQUEST({current_time})")
            for other in processes:
                if other != p:
                    print(f"  {p} -> {other} : REQUEST({current_time})")

        # ===== HANDLE REPLIES =====
        for p in time_groups[current_time]:
            for other in processes:
                if other == p:
                    continue

                if not processes[other]["active"]:
                    # inactive always replies
                    print(f"  {other} -> {p} : REPLY (idle)")
                    processes[p]["replies"].add(other)

                elif state[other] == "RELEASED":
                    print(f"  {other} -> {p} : REPLY")
                    processes[p]["replies"].add(other)

                elif state[other] == "HELD":
                    print(f"  {other} defers reply to {p}")
                    processes[other]["deferred"].add(p)

                elif state[other] == "WANTED":
                    other_t = processes[other]["time"]

                    if (other_t, other) < (current_time, p):
                        print(f"  {other} defers reply to {p}")
                        processes[other]["deferred"].add(p)
                    else:
                        print(f"  {other} -> {p} : REPLY")
                        processes[p]["replies"].add(other)

        print("\n📌 Queue:", global_queue)

        # ===== CS EXECUTION =====
        while global_queue:

            t, p = global_queue[0]

            if state[p] != "WANTED":
                global_queue.pop(0)
                continue

            if len(processes[p]["replies"]) < n - 1:
                break

            print(f"\n🟡 BEFORE ENTER → States:", state)

            # ENTER
            print(f"\n✅ {p} ENTERS CS")
            state[p] = "HELD"
            timeline.append((p, "ENTER"))

            print("🔎 States (after ENTER):", state)
            print(f"{p} is executing...")

            # EXIT
            print(f"❎ {p} EXITS CS")
            timeline.append((p, "EXIT"))
            state[p] = "RELEASED"

            print("🔎 States (after EXIT):", state)

            # RELEASE
            for other in processes:
                if other != p:
                    print(f"  {p} -> {other} : RELEASE")

            # DEFERRED REPLIES
            if processes[p]["deferred"]:
                print(f"  {p} sending deferred replies:")
                for d in processes[p]["deferred"]:
                    print(f"    {p} -> {d} : REPLY (deferred)")
                    processes[d]["replies"].add(p)

            processes[p]["deferred"].clear()
            processes[p]["replies"].clear()

            global_queue.pop(0)

    print("\n===== FINAL TIMELINE =====")
    for t in timeline:
        print(f"{t[0]} {t[1]}")

    print("\n✔ No overlap in critical section\n")

def manual_mutex():
    print("\n===== Manual Simulation =====\n")

    try:
        n = int(input("Enter number of processes: "))
    except:
        print("Invalid input\n")
        return

    processes = {
        f"P{i}": {
            "clock": 0,
            "state": "RELEASED",
            "request_time": None,
            "replies": set(),
            "deferred": set(),
            "sent_replies": set(),          # 🔥 NEW
            "received_requests": set()      # 🔥 NEW
        }
        for i in range(1, n+1)
    }

    print("\nCommands:")
    print("request P1 5")
    print("receive_request P2 P1")
    print("receive_reply P1 P2")
    print("release P1")
    print("(done to exit)\n")

    while True:
        entry = input("Event: ").strip()
        if entry.lower() == "done":
            break

        parts = entry.split()
        parts = [p.upper() for p in parts]

        try:
            # ===== REQUEST =====
            if parts[0] == "REQUEST":
                if len(parts) != 3:
                    print("❌ Format: request P1 5")
                    continue

                p = parts[1]
                t = int(parts[2])

                if p not in processes:
                    print("❌ Invalid process")
                    continue

                processes[p]["clock"] = t
                processes[p]["state"] = "WANTED"
                processes[p]["request_time"] = t
                processes[p]["replies"].clear()

                print(f"{p} REQUEST at time {t}")

            # ===== RECEIVE REQUEST =====
            elif parts[0] == "RECEIVE_REQUEST":
                if len(parts) != 3:
                    print("❌ Format: receive_request P2 P1")
                    continue

                r, s = parts[1], parts[2]

                if r not in processes or s not in processes:
                    print("❌ Invalid process name")
                    continue

                if r == s:
                    print("❌ Process cannot send request to itself")
                    continue

                rp = processes[r]
                sp = processes[s]

                rp["received_requests"].add(s)   # 🔥 TRACK

                rp["clock"] = max(rp["clock"], sp["clock"]) + 1

                if rp["state"] == "HELD" or (
                    rp["state"] == "WANTED" and
                    (rp["request_time"], r) < (sp["request_time"], s)
                ):
                    print(f"{r} defers reply to {s}")
                    rp["deferred"].add(s)
                else:
                    print(f"{r} -> {s} : REPLY")
                    rp["sent_replies"].add(s)   # 🔥 TRACK

            # ===== RECEIVE REPLY =====
            elif parts[0] == "RECEIVE_REPLY":
                if len(parts) != 3:
                    print("❌ Format: receive_reply P1 P2")
                    continue

                r, s = parts[1], parts[2]

                if r not in processes or s not in processes:
                    print("❌ Invalid process name")
                    continue

                if r == s:
                    print("❌ Process cannot receive reply from itself")
                    continue

                # 🔥 CRITICAL VALIDATION
                if r not in processes[s]["sent_replies"]:
                    print(f"❌ {s} never sent REPLY to {r}")
                    continue

                if s in processes[r]["replies"]:
                    print(f"❌ Duplicate reply from {s}")
                    continue

                processes[r]["replies"].add(s)

                print(f"{r} received REPLY from {s} ({len(processes[r]['replies'])}/{n-1})")

                if len(processes[r]["replies"]) == n - 1:
                    print(f"✅ {r} ENTERS CS")
                    processes[r]["state"] = "HELD"

            # ===== RELEASE =====
            elif parts[0] == "RELEASE":
                if len(parts) != 2:
                    print("❌ Format: release P1")
                    continue

                p = parts[1]

                if p not in processes:
                    print("❌ Invalid process name")
                    continue

                if processes[p]["state"] != "HELD":
                    print(f"❌ {p} cannot RELEASE (not in CS)")
                    continue

                print(f"\n🔴 {p} EXITING CS")

                print("🔎 Before EXIT:")
                for k, v in processes.items():
                    print(f"  {k}: state={v['state']}")

                processes[p]["state"] = "RELEASED"

                if processes[p]["deferred"]:
                    print(f"\n📤 {p} sending deferred replies:")
                    for d in processes[p]["deferred"]:
                        print(f"  {p} -> {d} : REPLY (deferred)")
                        processes[d]["replies"].add(p)

                processes[p]["deferred"].clear()
                processes[p]["replies"].clear()
                processes[p]["request_time"] = None

                print(f"\n✅ {p} is now RELEASED")

                print("🔎 After EXIT:")
                for k, v in processes.items():
                    print(f"  {k}: state={v['state']}")

            else:
                print("❌ Invalid command")

            # ===== PRINT STATES =====
            print("🔎 Detailed States:")
            for k, v in processes.items():
                print(
                    f"  {k}: state={v['state']} | "
                    f"replies={v['replies']} | "
                    f"deferred={v['deferred']} | "
                    f"sent={v['sent_replies']}"
                )
            print()

        except Exception as e:
            print(f"❌ Error: {e}\n")