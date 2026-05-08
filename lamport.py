
def handle_clock():
    print("\n===== Lamport Clock Simulation =====\n")

    try:
        n = int(input("Enter number of processes: "))
    except:
        print("Invalid input...\n Returning to menu...\n")
        return

    # Initialize processes
    processes = {f"P{i}": 0 for i in range(1, n+1)}
    print("\nInitialized Processes:", ", ".join(processes.keys()), "\n")

    messages = {}
    happens_before = []
    event_log = []   

    print("Enter events one by one...")
    print("Format examples:")
    print("\tlocal P1")
    print("\tsend P1 P2 M1")
    print("\treceive P2 P1 M1\n")
    print("(Type 'done' when finished)\n")

    while True:
        entry = input("Event: ").strip()

        if entry.lower() == "done":
            break

        parts = entry.split()
        parts = [p.upper() for p in parts]

        if len(parts) < 2:
            print("\t❌ Invalid event format\n")
            continue

        try:
            # ================= LOCAL =================
            if parts[0] == "LOCAL":
                if len(parts) != 2:
                    print("\t❌ Format: local P1\n")
                    continue

                _, p = parts

                if p not in processes:
                    print(f"\t❌ Process {p} does not exist")
                    print(f"\t❌ Valid range: P1 to P{n}\n")
                    continue

                processes[p] += 1

                print(f"\t{p} | LOCAL | Clock = {processes[p]}\n")

                event_log.append(f"{p} LOCAL → Clock {processes[p]}")

            # ================= SEND =================
            elif parts[0] == "SEND":
                if len(parts) != 4:
                    print("\t❌ Format: send P1 P2 M1\n")
                    continue

                _, sender, receiver, msg = parts

                if sender not in processes or receiver not in processes:
                    print("\t❌ Invalid sender/receiver\n")
                    continue

                if sender == receiver:
                    print("\t❌ Sender and receiver cannot be same\n")
                    continue

                if not msg.startswith("M"):
                    print("\t❌ Message must be like M1, M2...\n")
                    continue

                if msg in messages:
                    print("\t❌ Message ID already exists\n")
                    continue

                processes[sender] += 1
                timestamp = processes[sender]

                messages[msg] = {
                    "sender": sender,
                    "receiver": receiver,
                    "timestamp": timestamp
                }

                # ✅ Happens-before stored here
                happens_before.append(f"{sender} → {receiver} ({msg})")

                print(f"\t{sender} -> {receiver} | SEND {msg}")
                print(f"\tTimestamp attached: {timestamp}\n")

                event_log.append(
                    f"{sender} SEND {msg} → {receiver} (ts={timestamp})"
                )

            # ================= RECEIVE =================
            elif parts[0] == "RECEIVE":
                if len(parts) != 4:
                    print("\t❌ Format: receive P2 P1 M1\n")
                    continue

                _, receiver, sender, msg = parts

                if receiver not in processes or sender not in processes:
                    print("\t❌ Invalid sender/receiver\n")
                    continue

                if msg not in messages:
                    print("\t❌ Message not found\n")
                    continue

                msg_data = messages[msg]

                if msg_data["sender"] != sender or msg_data["receiver"] != receiver:
                    print("\t❌ Message sender/receiver mismatch\n")
                    continue

                recv_time = msg_data["timestamp"]
                old_clock = processes[receiver]

                new_clock = max(old_clock, recv_time) + 1
                processes[receiver] = new_clock

                print(f"\t{receiver} <- {sender} | RECEIVE {msg}")
                print(f"\tRule: max({old_clock}, {recv_time}) + 1 = {new_clock}")

                print()

                event_log.append(
                    f"{receiver} RECEIVE {msg} ← {sender} "
                    f"(ts={recv_time}) → Clock {new_clock}"
                )

            else:
                print("\t❌ Invalid event type\n")

        except Exception as e:
            print(f"\t❌ Unexpected error: {e}\n")

    # ================= FINAL SUMMARY =================

    print("\n" + "="*50)
    print("📜 EXECUTION SUMMARY")
    print("="*50)

    print("\n--- Event History ---")
    for i, e in enumerate(event_log, 1):
        print(f"{i}. {e}")

    print("\n--- Final Clock Values ---")
    for p in processes:
        print(f"{p}: {processes[p]}")

    print("\n--- Happens-Before Relationships ---")
    if happens_before:
        for hb in happens_before:
            print(hb)
    else:
        print("None")

    print("\nSystem execution completed successfully.\n")

def lamport_generate_steps(events, n):
    processes = {f"P{i}": 0 for i in range(1, n+1)}
    messages = {}

    steps = []
    errors = []

    event_log = []
    happens_before = []

    steps.append({
        "text": "Initial State (All clocks = 0)",
        "clocks": processes.copy()
    })

    def add_step(text):
        steps.append({
            "text": text,
            "clocks": processes.copy()
        })

    for line_no, entry in enumerate(events, 1):
        parts = entry.strip().split()
        parts = [p.upper() for p in parts]

        if not parts:
            continue

        try:
            # ===== LOCAL =====
            if parts[0] == "LOCAL":
                if len(parts) != 2:
                    errors.append(f"❌ Line {line_no}: Format → local P1")
                    continue

                _, p = parts

                if p not in processes:
                    errors.append(f"❌ Line {line_no}: Process {p} does not exist")
                    errors.append(f"❌ Line {line_no}: Valid range → P1 to P{n}")
                    continue

                processes[p] += 1
                text = f"{p} LOCAL → Clock {processes[p]}"
                add_step(text)
                event_log.append(text)

            # ===== SEND =====
            elif parts[0] == "SEND":
                if len(parts) != 4:
                    errors.append(f"❌ Line {line_no}: Format → send P1 P2 M1")
                    continue

                _, sender, receiver, msg = parts

                if sender not in processes or receiver not in processes:
                    errors.append(f"❌ Line {line_no}: Invalid sender/receiver")
                    continue

                if sender == receiver:
                    errors.append(f"❌ Line {line_no}: Sender and receiver cannot be same")
                    continue

                if not msg.startswith("M"):
                    errors.append(f"❌ Line {line_no}: Message must be like M1, M2,...")
                    continue

                if msg in messages:
                    errors.append(f"❌ Line {line_no}: Message ID already exists")
                    continue

                processes[sender] += 1
                timestamp = processes[sender]

                messages[msg] = {
                    "sender": sender,
                    "receiver": receiver,
                    "timestamp": timestamp
                }

                happens_before.append(f"{sender} → {receiver} ({msg})")

                text = f"{sender} SEND {msg} → {receiver} (ts={timestamp})"
                add_step(text)
                event_log.append(text)

            # ===== RECEIVE =====
            elif parts[0] == "RECEIVE":
                if len(parts) != 4:
                    errors.append(f"❌ Line {line_no}: Format → receive P2 P1 M1")
                    continue

                _, receiver, sender, msg = parts

                if msg not in messages:
                    errors.append(f"❌ Line {line_no}: Message {msg} not found")
                    continue

                msg_data = messages[msg]

                if msg_data["sender"] != sender or msg_data["receiver"] != receiver:
                    errors.append(f"❌ Line {line_no}: Message sender/receiver mismatch")
                    continue

                recv_time = msg_data["timestamp"]
                old = processes[receiver]

                new_clock = max(old, recv_time) + 1
                processes[receiver] = new_clock

                text = f"{receiver} RECEIVE {msg} ← {sender} → Clock {new_clock}"
                add_step(text)
                event_log.append(text)

            else:
                errors.append(f"❌ Line {line_no}: Invalid event type")

        except Exception as e:
            errors.append(f"❌ Line {line_no}: Unexpected error")

    return steps, errors, event_log, happens_before, processes