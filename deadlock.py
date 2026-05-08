def handle_deadlock():
    print("\n===== Deadlock Detection & Recovery =====\n")

    # ===== INPUT =====
    try:
        n = int(input("Enter number of processes: "))
    except:
        print("Invalid input\n")
        return

    processes = [f"P{i}" for i in range(1, n+1)]
    graph = {p: [] for p in processes}
    priority = {}

    print("\nEnter wait-for edges (format: P1 P2 means P1 waits for P2)")
    print("Type 'done' when finished\n")

    while True:
        entry = input("Edge: ").strip()
        if entry.lower() == "done":
            break

        parts = entry.upper().split()

        if len(parts) != 2:
            print("❌ Format: P1 P2")
            continue

        u, v = parts

        if u not in graph or v not in graph:
            print("❌ Invalid process")
            continue

        if v in graph[u]:
            print("⚠️ Duplicate edge ignored")
            continue

        graph[u].append(v)

    print("\nEnter priority values (higher number = killed first)")

    for p in processes:
        try:
            priority[p] = int(input(f"{p}: "))
        except:
            print("Invalid priority\n")
            return

    # ===== PRINT GRAPH =====
    print("\n===== WAIT-FOR GRAPH =====")
    for p in graph:
        print(f"{p} -> {graph[p]}")

    # ===== CYCLE DETECTION =====
    def normalize_cycle(cycle):
        """Normalize cycle to avoid duplicates"""
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

    # ===== MAIN LOOP =====
    terminated = []
    all_cycles_detected = []

    while True:
        cycles = find_cycles(graph)

        if not cycles:
            break

        # store all cycles for final reporting
        all_cycles_detected.extend(cycles)

        print("\n🔴 Deadlock Cycles Detected:")
        for i, c in enumerate(cycles, 1):
            print(f"Cycle {i}: {' -> '.join(c)} -> {c[0]}")

        # resolve cycles
        for cycle in cycles:
            victim = max(cycle, key=lambda x: priority[x])

            print(f"\n⚡ Terminating {victim} (priority {priority[victim]})")

            if victim not in terminated:
                terminated.append(victim)

            # remove node
            graph[victim] = []

            for p in graph:
                if victim in graph[p]:
                    graph[p].remove(victim)

        print("\n📌 Updated Graph:")
        for p in graph:
            print(f"{p} -> {graph[p]}")

    # ===== FINAL REPORT =====
    print("\n===== FINAL REPORT =====")

    if terminated:
        print("Terminated Processes:", terminated)
    else:
        print("No processes terminated")

    print("\nFinal Graph:")
    for p in graph:
        print(f"{p} -> {graph[p]}")

    # ===== SAFE NODES =====
    print("\n🟢 Safe Chains (not part of any deadlock):")

    all_cycle_nodes = set()
    for c in all_cycles_detected:
        all_cycle_nodes.update(c)

    for p in processes:
        if p not in all_cycle_nodes:
            print(f"{p} is NOT part of any deadlock")

    print("\n✅ System is deadlock-free\n")