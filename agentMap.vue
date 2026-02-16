<template>
  <div class="min-h-screen bg-slate-950 text-slate-100 p-6">
    <div class="max-w-7xl mx-auto space-y-6">
      <header class="space-y-1">
        <h1 class="text-2xl font-semibold">Agente Inteligente — Mapa + Recompensas</h1>
        <p class="text-slate-300 text-sm">
          Selecciona estado inicial y meta. Se calcula una ruta (por ahora BFS) y se construye la matriz R (recompensas).
        </p>
      </header>

      <!-- Controles -->
      <section class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-4">
          <h2 class="font-semibold">Controles</h2>

          <div class="space-y-2">
            <label class="text-sm text-slate-300">Inicio</label>
            <select v-model="start" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 outline-none focus:ring-2 focus:ring-sky-500">
              <option v-for="s in states" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>

          <div class="space-y-2">
            <label class="text-sm text-slate-300">Meta</label>
            <select v-model="goal" class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 outline-none focus:ring-2 focus:ring-emerald-500">
              <option v-for="s in states" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>

          <div class="flex gap-3">
            <button @click="calcRoute"
              class="flex-1 rounded-xl bg-sky-600 hover:bg-sky-500 active:bg-sky-700 px-4 py-2 font-medium">
              Calcular ruta
            </button>
            <button @click="resetAll"
              class="flex-1 rounded-xl bg-slate-800 hover:bg-slate-700 active:bg-slate-900 px-4 py-2 font-medium">
              Reset
            </button>
          </div>

          <div class="bg-slate-950 border border-slate-800 rounded-2xl p-4">
            <div class="text-sm text-slate-300 mb-2">Ruta</div>
            <div class="font-mono text-sm break-words">
              <span v-if="route.length">{{ route.join(' → ') }}</span>
              <span v-else class="text-slate-400">—</span>
            </div>
            <p v-if="warn" class="text-rose-300 text-sm mt-2">{{ warn }}</p>
          </div>

          <div class="text-xs text-slate-400">
            Nota: la tabla R depende de la meta. Cuando cambias meta, cambian las recompensas 100 hacia esa meta.
          </div>
        </div>

        <!-- Mapa -->
        <div class="lg:col-span-2 bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
          <div class="flex items-center justify-between mb-3">
            <h2 class="font-semibold">Mapa</h2>
            <span class="text-xs text-slate-400">SVG</span>
          </div>

          <div class="overflow-auto rounded-2xl border border-slate-800 bg-slate-950">
            <svg :width="900" :height="520" viewBox="0 0 900 520" class="block">
              <!-- aristas base -->
              <g>
                <line
                  v-for="(e, i) in edges"
                  :key="`edge-${i}`"
                  :x1="pos[e[0]][0]" :y1="pos[e[0]][1]"
                  :x2="pos[e[1]][0]" :y2="pos[e[1]][1]"
                  class="stroke-slate-600/70"
                  stroke-linecap="round"
                  :stroke-width="3"
                />
              </g>

              <!-- ruta resaltada -->
              <g v-if="route.length >= 2">
                <line
                  v-for="(seg, i) in routeSegments"
                  :key="`path-${i}`"
                  :x1="pos[seg[0]][0]" :y1="pos[seg[0]][1]"
                  :x2="pos[seg[1]][0]" :y2="pos[seg[1]][1]"
                  class="stroke-amber-300/90"
                  stroke-linecap="round"
                  :stroke-width="7"
                />
              </g>

              <!-- nodos -->
              <g v-for="s in states" :key="`node-${s}`">
                <circle
                  :cx="pos[s][0]" :cy="pos[s][1]" r="18"
                  :class="nodeClass(s)"
                  :stroke-width="(s===start || s===goal) ? 3 : 2"
                />
                <text
                  :x="pos[s][0]" :y="pos[s][1]"
                  text-anchor="middle"
                  dominant-baseline="middle"
                  class="fill-slate-100 font-semibold"
                  style="font-size: 12px;"
                >
                  {{ s }}
                </text>
              </g>

              <!-- agente -->
              <circle
                :cx="pos[start][0]" :cy="pos[start][1]" r="10"
                class="fill-sky-300"
              />
            </svg>
          </div>
        </div>
      </section>
      <section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
  <div class="flex items-center justify-between mb-4">
    <div>
      <h2 class="font-semibold">Matriz de adyacencia (A)</h2>
      <p class="text-sm text-slate-300">1 = hay conexión, 0 = no hay conexión</p>
    </div>
  </div>

  <div class="overflow-auto rounded-2xl border border-slate-800 bg-slate-950">
    <table class="min-w-[900px] w-full text-sm">
      <thead class="sticky top-0 bg-slate-950">
        <tr>
          <th class="text-left p-2 border-b border-slate-800">A</th>
          <th v-for="c in states" :key="`a-col-${c}`" class="p-2 border-b border-slate-800 text-center">
            {{ c }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in states" :key="`a-row-${r}`" class="odd:bg-slate-900/20">
          <td class="p-2 border-b border-slate-800 font-semibold">{{ r }}</td>
          <td
            v-for="c in states"
            :key="`a-cell-${r}-${c}`"
            class="p-2 border-b border-slate-800 text-center font-mono"
          >
            <span :class="adjacencyMatrix[r][c] ? 'text-slate-100' : 'text-slate-600'">
              {{ adjacencyMatrix[r][c] }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</section>


      <!-- Recompensas: Vista entendible -->
      <section class="bg-slate-900/60 border border-slate-800 rounded-2xl p-5">
        <div class="flex items-center justify-between gap-4 mb-4">
          <div class="space-y-1">
            <h2 class="font-semibold">Tabla de recompensas (R)</h2>
            <p class="text-sm text-slate-300">
              Vista entendible: solo se muestran acciones válidas. <span class="text-emerald-300">100</span> si la acción llega a la meta.
            </p>
          </div>

          <div class="flex gap-2">
            <button
              @click="rView = 'lista'"
              class="rounded-xl px-3 py-2 text-sm border"
              :class="rView === 'lista' ? 'bg-slate-950 border-slate-700' : 'bg-slate-900 border-slate-800 hover:border-slate-700'"
            >
              Lista (recomendada)
            </button>
            <button
              @click="rView = 'matriz'"
              class="rounded-xl px-3 py-2 text-sm border"
              :class="rView === 'matriz' ? 'bg-slate-950 border-slate-700' : 'bg-slate-900 border-slate-800 hover:border-slate-700'"
            >
              Matriz
            </button>
          </div>
        </div>

        <!-- LISTA -->
        <div v-if="rView === 'lista'" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          <div
            v-for="row in rewardList"
            :key="`r-${row.state}`"
            class="bg-slate-950 border border-slate-800 rounded-2xl p-4"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="font-semibold">{{ row.state }}</div>
              <div class="text-xs text-slate-400">acciones: {{ row.actions.length }}</div>
            </div>

            <div v-if="row.actions.length" class="space-y-2">
              <div
                v-for="a in row.actions"
                :key="`${row.state}-${a.to}`"
                class="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-900/40 px-3 py-2"
              >
                <div class="font-mono text-sm">
                  {{ row.state }} → {{ a.to }}
                </div>
                <div
                  class="text-sm font-semibold"
                  :class="a.reward === 100 ? 'text-emerald-300' : 'text-slate-200'"
                >
                  {{ a.reward }}
                </div>
              </div>
            </div>

            <div v-else class="text-sm text-slate-400">Sin acciones (no debería pasar en este grafo).</div>
          </div>
        </div>

        <!-- MATRIZ -->
        <div v-else class="overflow-auto rounded-2xl border border-slate-800 bg-slate-950">
          <table class="min-w-[900px] w-full text-sm">
            <thead class="sticky top-0 bg-slate-950">
              <tr>
                <th class="text-left p-2 border-b border-slate-800">R</th>
                <th v-for="c in states" :key="`col-${c}`" class="p-2 border-b border-slate-800 text-center">
                  {{ c }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in states" :key="`row-${r}`" class="odd:bg-slate-900/20">
                <td class="p-2 border-b border-slate-800 font-semibold">{{ r }}</td>

                <td
                  v-for="c in states"
                  :key="`cell-${r}-${c}`"
                  class="p-2 border-b border-slate-800 text-center font-mono"
                >
                  <span
                    v-if="rewardMatrix[r][c] === null"
                    class="text-slate-600"
                  >
                    —
                  </span>

                  <span
                    v-else
                    :class="rewardMatrix[r][c] === 100 ? 'text-emerald-300 font-semibold' : 'text-slate-200'"
                  >
                    {{ rewardMatrix[r][c] }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="mt-4 text-xs text-slate-400">
          Convención: <span class="text-slate-200">-1</span> = costo por moverse, <span class="text-emerald-300">100</span> = llegar a la meta, <span class="text-slate-600">—</span> = transición inválida.
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
const adjacencyMatrix = computed(() => {
  const m = {};
  for (const r of states) {
    m[r] = {};
    for (const c of states) m[r][c] = 0;
  }
  for (const [u, v] of edges) {
    m[u][v] = 1;
    m[v][u] = 1;
  }
  return m;
});

import { computed, ref, watch } from "vue";

/** Estados */
const states = [..."ABCDEFGHIJKLMNOPQRST"];

/** Aristas (mismo grafo que tu Python) */
const edges = [
  ["A","B"],
  ["B","C"], ["B","D"],
  ["C","J"], ["J","O"], ["C","M"],
  ["M","N"],
  ["N","L"], ["L","H"], ["N","G"],
  ["G","I"],
  ["I","R"], ["I","P"],
  ["P","S"], ["S","Q"], ["Q","T"],
  ["K","E"], ["K","F"], ["K","P"],
  ["F","Q"],
];

/** Posiciones para el mapa (ajustables) */
const pos = {
  A:[90,80],  B:[210,80], D:[320,80],
  C:[160,160], M:[280,160],
  J:[160,250], O:[60,250],
  H:[120,330], L:[240,330],
  N:[360,240], G:[450,320],
  I:[560,320], R:[650,250],
  P:[560,420], S:[650,420],
  Q:[760,460], T:[760,480],
  K:[360,460], E:[260,460], F:[480,470]
};

const start = ref("A");
const goal = ref("T");
const route = ref([]);
const warn = ref("");
const rView = ref("lista"); // 'lista' | 'matriz'

/** Lista de adyacencia */
const adj = computed(() => {
  const m = new Map(states.map(s => [s, []]));
  for (const [u, v] of edges) {
    m.get(u).push(v);
    m.get(v).push(u);
  }
  return m;
});

/** BFS (ruta más corta) — por ahora para UI */
function bfsPath(s, g) {
  if (s === g) return [s];
  const q = [s];
  const prev = new Map([[s, null]]);
  while (q.length) {
    const u = q.shift();
    for (const v of adj.value.get(u)) {
      if (!prev.has(v)) {
        prev.set(v, u);
        if (v === g) {
          const path = [];
          let cur = g;
          while (cur !== null) { path.push(cur); cur = prev.get(cur); }
          path.reverse();
          return path;
        }
        q.push(v);
      }
    }
  }
  return null;
}

function calcRoute() {
  warn.value = "";
  const p = bfsPath(start.value, goal.value);
  if (!p) {
    route.value = [];
    warn.value = "No existe ruta entre esos estados en el grafo.";
    return;
  }
  route.value = p;
}

function resetAll() {
  start.value = "A";
  goal.value = "T";
  warn.value = "";
  route.value = [];
  calcRoute();
}

/** Segmentos para dibujar la ruta */
const routeSegments = computed(() => {
  const p = route.value;
  const segs = [];
  for (let i = 0; i < p.length - 1; i++) segs.push([p[i], p[i+1]]);
  return segs;
});

function nodeClass(s) {
  if (s === start.value) return "fill-sky-600 stroke-sky-200";
  if (s === goal.value) return "fill-emerald-600 stroke-emerald-200";
  return "fill-slate-900 stroke-slate-300";
}

/**
 * MATRIZ R entendible:
 * - null = inválida (equivalente a -inf)
 * - -1 = movimiento válido
 * - 100 = movimiento válido hacia meta
 */
const rewardMatrix = computed(() => {
  const m = {};
  for (const r of states) {
    m[r] = {};
    for (const c of states) m[r][c] = null;
  }

  // acciones válidas (base = -1)
  for (const [u, v] of edges) {
    m[u][v] = -1;
    m[v][u] = -1;
  }

  // hacia meta = 100 SOLO si existe arista
  for (const s of states) {
    if (m[s][goal.value] !== null) {
      m[s][goal.value] = 100;
    }
  }

  return m;
});

/** Vista lista (por estado -> acciones válidas) */
const rewardList = computed(() => {
  return states.map(s => {
    const actions = adj.value.get(s).map(to => ({
      to,
      reward: rewardMatrix.value[s][to]
    }));
    return { state: s, actions };
  });
});

/** Recalcular ruta automáticamente si cambian inicio/meta */
watch([start, goal], () => {
  // Si el usuario ya tenía ruta calculada, la recalculamos
  if (route.value.length) calcRoute();
});

// Init
calcRoute();
</script>
