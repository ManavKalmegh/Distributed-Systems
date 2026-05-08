import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

def run_deadlock_ui():

    st.title("🔒 Deadlock Detection & Recovery")

    # =============================
    # INPUT
    # =============================
    n = st.number_input("Number of Processes", min_value=1, step=1)
    processes = [f"P{i}" for i in range(1, n + 1)]

    st.markdown("### 🔗 Wait-For Edges")

    if "edges" not in st.session_state:
        st.session_state.edges = []

    col1, col2 = st.columns(2)
    u = col1.selectbox("From (Waiting)", processes, key="u_dl")
    v = col2.selectbox("To (Holding)", processes, key="v_dl")

    if st.button("➕ Add Edge"):
        if u == v:
            st.error("❌ Process cannot wait for itself")
        elif (u, v) in st.session_state.edges:
            st.warning("⚠️ Duplicate edge ignored")
        else:
            st.session_state.edges.append((u, v))
            st.success(f"✅ Added: {u} → {v}")

    if st.button("🧹 Clear Edges"):
        st.session_state.edges = []

    # =============================
    # GRAPH BUILD
    # =============================
    graph = {p: [] for p in processes}
    for (a, b) in st.session_state.edges:
        graph[a].append(b)

    # =============================
    # GRAPH VISUALIZATION 🔥
    # =============================
    st.markdown("### 🧠 Wait-For Graph")

    def draw_graph(graph, highlight_nodes=None):
        import networkx as nx
        import matplotlib.pyplot as plt

        G = nx.DiGraph()

        for p in graph:
            G.add_node(p)
            for nei in graph[p]:
                G.add_edge(p, nei)

        # 🔥 Better layout scaling
        pos = nx.circular_layout(G, scale=2)

        plt.figure(figsize=(6, 6))
        ax = plt.gca()

        node_colors = []
        for node in G.nodes():
            if highlight_nodes and node in highlight_nodes:
                node_colors.append("red")
            else:
                node_colors.append("#8fbcd4")

        nx.draw(
            G,
            pos,
            with_labels=True,
            node_color=node_colors,
            node_size=2500,
            font_size=10,
            arrows=True,
            ax=ax
        )

        # FIX: lock axis limits (prevents cutoff)
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)

        ax.set_aspect('equal')
        ax.axis('off')

        st.pyplot(plt)

    draw_graph(graph)

    # =============================
    # PRIORITY INPUT
    # =============================
    st.markdown("### ⚖️ Priority (higher = killed first)")

    priority = {}
    cols = st.columns(len(processes))

    for i, p in enumerate(processes):
        priority[p] = cols[i].number_input(f"{p}", value=1, key=f"prio_{p}")

    # =============================
    # VALIDATION
    # =============================
    if st.button("🚀 Run Deadlock Detection"):

        if not st.session_state.edges:
            st.error("❌ No edges provided — no deadlock possible")
            return

        # =============================
        # HELPERS
        # =============================
        def normalize_cycle(cycle):
            min_node = min(cycle)
            idx = cycle.index(min_node)
            return tuple(cycle[idx:] + cycle[:idx])

        def find_cycles(graph):
            visited = set()
            stack = []
            cycles = set()

            def dfs(node):
                visited.add(node)
                stack.append(node)

                for nei in graph[node]:
                    if nei not in visited:
                        dfs(nei)
                    elif nei in stack:
                        idx = stack.index(nei)
                        cycle = stack[idx:].copy()
                        cycles.add(normalize_cycle(cycle))

                stack.pop()

            for p in graph:
                if p not in visited:
                    dfs(p)

            return [list(c) for c in cycles]

        # =============================
        # STEP-BY-STEP EXECUTION 🔥
        # =============================
        graph_copy = {p: graph[p][:] for p in graph}
        terminated = []
        all_cycles = []

        st.markdown("## 🔍 Detection Steps")

        step = 1

        while True:
            cycles = find_cycles(graph_copy)

            if not cycles:
                st.success("✅ No more cycles → System safe")
                break

            all_cycles.extend(cycles)

            st.markdown(f"### ⚠️ Step {step}: Deadlock Detected")

            for i, c in enumerate(cycles, 1):
                st.error(f"Cycle {i}: {' → '.join(c)} → {c[0]}")

            # highlight cycles
            cycle_nodes = set()
            for c in cycles:
                cycle_nodes.update(c)

            draw_graph(graph_copy, highlight_nodes=cycle_nodes)

            # =============================
            # RESOLUTION
            # =============================
            for cycle in cycles:
                victim = max(cycle, key=lambda x: priority[x])

                st.warning(f"⚡ Terminating {victim} (priority {priority[victim]})")

                if victim not in terminated:
                    terminated.append(victim)

                graph_copy[victim] = []

                for p in graph_copy:
                    if victim in graph_copy[p]:
                        graph_copy[p].remove(victim)

            st.markdown("### 🔄 Graph After Removal")
            draw_graph(graph_copy)

            step += 1

        # =============================
        # FINAL REPORT
        # =============================
        st.markdown("## 📊 Final Report")

        if terminated:
            st.error(f"❌ Terminated: {terminated}")
        else:
            st.success("No process terminated")

        st.markdown("### 🟢 Safe Processes")

        dead_nodes = set()
        for c in all_cycles:
            dead_nodes.update(c)

        safe = [p for p in processes if p not in dead_nodes]

        if safe:
            for p in safe:
                st.success(f"{p} is SAFE")
        else:
            st.warning("No safe processes")