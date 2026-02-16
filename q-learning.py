import numpy as np

# ============================
# DEFINICIÓN DEL ENTORNO
# ============================

states = list("ABCDEFGHIJKLMNOPQRST")
n = len(states)

state_index = {s:i for i,s in enumerate(states)}
index_state = {i:s for i,s in enumerate(states)}

# Matriz de recompensas base
R_base = np.full((n, n), -np.inf)

# ============================
# MOSTRAR MATRIZ DE ADYACENCIA
# ============================

def mostrar_matriz_adyacencia():

    print("\nMATRIZ DE ADYACENCIA:\n")

    # encabezado columnas
    print("   ", end="")
    for s in states:
        print(f"{s:3}", end="")
    print()

    for i in range(n):

        # encabezado fila
        print(f"{states[i]:3}", end="")

        for j in range(n):

            if np.isfinite(R_base[i, j]):
                print(" 1 ", end="")
            else:
                print(" 0 ", end="")

        print()


def connect(a, b, reward=-1):
    i, j = state_index[a], state_index[b]
    R_base[i, j] = reward
    R_base[j, i] = reward

# Conexiones
connect("A","B")
connect("B","C")
connect("B","D")
connect("C","J")
connect("J","O")
connect("C","M")
connect("M","N")
connect("N","L")
connect("L","H")
connect("N","G")
connect("G","I")
connect("I","R")
connect("I","P")
connect("P","S")
connect("S","Q")
connect("Q","T")
connect("K","E")
connect("K","F")
connect("K","P")
connect("F","Q")

# ============================
# FUNCIÓN Q-LEARNING
# ============================

def entrenar(goal_i):

    R = R_base.copy()

    # recompensa meta solo si existe conexión
    for s in range(n):
        if np.isfinite(R[s, goal_i]):
            R[s, goal_i] = 100

    Q = np.zeros((n,n))

    alpha = 0.2
    gamma = 0.9
    epsilon = 0.2
    episodes = 8000

    rng = np.random.default_rng()

    def acciones_validas(s):
        return np.where(np.isfinite(R[s]))[0]

    for _ in range(episodes):

        s = rng.integers(0, n)

        if s == goal_i:
            continue

        for _ in range(200):

            acts = acciones_validas(s)

            if len(acts) == 0:
                break

            if rng.random() < epsilon:
                a = rng.choice(acts)
            else:
                a = acts[np.argmax(Q[s, acts])]

            Q[s,a] = (1-alpha)*Q[s,a] + alpha*(R[s,a] + gamma*np.max(Q[a]))

            s = a

            if s == goal_i:
                break

    return Q, R


# ============================
# FUNCIÓN OBTENER RUTA
# ============================

def obtener_ruta(Q, R, start_i, goal_i):

    def acciones_validas(s):
        return np.where(np.isfinite(R[s]))[0]

    current = start_i
    path = [index_state[current]]
    visitados = set([current])

    for _ in range(200):

        if current == goal_i:
            break

        acts = acciones_validas(current)

        next_state = acts[np.argmax(Q[current, acts])]

        if next_state in visitados:
            break

        visitados.add(next_state)
        path.append(index_state[next_state])
        current = next_state

    return path


# ============================
# BUCLE PRINCIPAL
# ============================
# ============================
# MOSTRAR MATRIZ DE RECOMPENSAS
# ============================

def mostrar_matriz_recompensas(R):

    print("\nMATRIZ DE RECOMPENSAS (R):\n")

    # encabezado
    print("   ", end="")
    for s in states:
        print(f"{s:4}", end="")
    print()

    for i in range(n):

        print(f"{states[i]:3}", end="")

        for j in range(n):

            valor = R[i, j]

            if np.isinf(valor):
                print(" -∞ ", end="")
            else:
                print(f"{int(valor):4}", end="")

        print()


while True:
    mostrar_matriz_adyacencia()


    print("\nEstados disponibles:")
    print(states)

    start = input("\nSelecciona estado inicial: ").upper()
    goal  = input("Selecciona estado meta: ").upper()

    if start not in states or goal not in states:
        print("Estado inválido.")
        continue

    start_i = state_index[start]
    goal_i  = state_index[goal]

    print("\nEntrenando agente...")

    Q, R = entrenar(goal_i)
    mostrar_matriz_recompensas(R)


    path = obtener_ruta(Q, R, start_i, goal_i)

    print("\nRuta óptima:")
    print(" → ".join(path))
    

    # ============================
    # PREGUNTAR SI QUIERE OTRA RUTA
    # ============================

    opcion = input("\n¿Deseas calcular otra ruta? (s/n): ").lower()

    if opcion != "s":
        print("\nPrograma finalizado.")
        break
