# 🧠 Distributed Systems Simulator

An interactive Python-based simulator for important Distributed Systems algorithms with both:

- 🖥️ Terminal (CLI) Version
- 🌐 Streamlit UI Version

The project focuses on visualization and understanding of distributed algorithms through interactive simulations and graphical representations.

---

# ✨ Features

- Interactive Streamlit UI
- Terminal-based simulations
- Step-by-step execution
- Timeline and graph visualizations
- Event logging
- Input validation
- Educational demonstrations for viva/labs

---

# 📂 Project Structure

```bash
.
├── main.py
├── lamport.py
├── lamport_ui.py
├── mutex.py
├── mutex_ui.py
├── deadlock.py
├── deadlock_ui.py
└── README.md
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone <your-repo-url>
cd <repo-name>
```

## Install Dependencies

```bash
pip install streamlit matplotlib networkx
```

---

# 🌐 Run Streamlit UI

```bash
streamlit run main.py
```

Open browser at:

```text
http://localhost:8501
```

---

# 🖥️ Run Terminal Versions

## Lamport Clock

```bash
python lamport.py
```

## Mutual Exclusion

```bash
python mutex.py
```

## Deadlock Detection

```bash
python deadlock.py
```

---

# 🧠 Algorithms Implemented

---

## 🕒 Lamport Logical Clock

Lamport clocks are used for logical ordering of events in distributed systems.

### Features
- Local events
- Send/Receive events
- Happens-before relationship
- Timeline visualization
- Event history tracking

### Example Input

```text
local P1
send P1 P2 M1
receive P2 P1 M1
```

---

## 🔐 Ricart–Agrawala Mutual Exclusion

Distributed mutual exclusion algorithm using REQUEST and REPLY messages.

### Features
- Auto simulation
- Manual simulation
- Deferred replies
- Critical section visualization
- Process state tracking

### Process States
- RELEASED
- WANTED
- HELD

---

## 🔒 Deadlock Detection & Recovery

Deadlock detection using Wait-For Graphs and cycle detection.

### Features
- Wait-for graph visualization
- Cycle detection
- Automatic recovery
- Safe process identification
- Deadlock-free verification

### Example Edge

```text
P1 P2
```

Meaning:
- P1 waits for P2

---

# 📸 UI Modules

## Lamport Clock UI
- Timeline visualization
- Logical clock updates
- Happens-before tracking

## Mutual Exclusion UI
- Process state animations
- Auto-play simulation
- Event logs

## Deadlock Detection UI
- Wait-for graph
- Cycle highlighting
- Recovery visualization

---
