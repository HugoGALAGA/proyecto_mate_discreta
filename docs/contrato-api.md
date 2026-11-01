# Contrato de la API (v1)

Servidor FastAPI de `src/api/app.py`. JSON en UTF-8, claves en español y `snake_case`.

**Reglas globales**
- **Todo el tiempo va en ticks enteros** (1 tick = `tick_segundos`, hoy 0.5 s). El frontend convierte a segundos solo para mostrar.
- Ids de nodo: enteros `0..n-1`. Ids de entidad: `"Z1"`, `"S1"`, `"Z2"`...
- Los modelos Pydantic de este contrato viven en `src/api/schemas.py` y son la única definición válida del formato.

---

## 1. Endpoints

| Método | Ruta | Uso |
|---|---|---|
| GET | `/api/health` | Ya existe. Devuelve `{"status": "ok"}`. |
| GET | `/api/parametros` | Límites que necesita React (no se escribe ningún número del juego en el frontend). |
| POST | `/api/simulate` | Corre una partida completa y devuelve todo. |

### GET /api/parametros
```json
{
  "version_contrato": 1,
  "tick_segundos": 0.5,
  "supervivientes_min": 3,
  "supervivientes_max": 5,
  "limite_partida_ticks": 240
}
```

### POST /api/simulate: solicitud
```json
{ "supervivientes": 4, "semilla": null, "modo_pruebas": false }
```
- `supervivientes`: entero entre `supervivientes_min` y `supervivientes_max`.
- `semilla`: entero `0 <= s < 2^53`, o `null`. Con `null`, el servidor genera una de 52 bits con entropía del sistema. El tope es 2^53 porque JavaScript pierde precisión con enteros mayores.
- `modo_pruebas`: `true` usa `limite_pruebas` (60 s) en vez de `limite_partida`. Solo para tests y E2E.

**Errores:** `422` (formato estándar de FastAPI) si un campo es inválido. `500` con `{"detail": "..."}` si no se logra generar un mapa válido en `intentos_max_generacion`.

---

## 2. POST /api/simulate: respuesta

```json
{
  "version_contrato": 1,
  "semilla": 4821937465021,
  "tick_segundos": 0.5,
  "limite_ticks": 240,
  "mapa": {
    "nodos": [
      { "id": 0, "tipo": "ZS", "x": 500, "y": 500 },
      { "id": 1, "tipo": "LS", "x": 430, "y": 470 },
      { "id": 2, "tipo": "L", "x": 120, "y": 880 }
    ],
    "aristas": [
      { "a": 0, "b": 1, "peso": 3, "cluster": "corto" },
      { "a": 1, "b": 2, "peso": 8, "cluster": "largo" }
    ]
  },
  "entidades": [
    { "id": "Z1", "tipo": "zombie", "nodo_inicial": 14 },
    { "id": "S1", "tipo": "superviviente", "nodo_inicial": 22 }
  ],
  "eventos": [],
  "resultados": {},
  "mst": {
    "aristas": [{ "a": 0, "b": 1, "peso": 3 }],
    "peso_total": 57
  }
}
```

- **`mapa.nodos`:** `tipo` es `"L"`, `"LS"` o `"ZS"`. `x` e `y` van de 0 a 1000. **Las posiciones las calcula Python** (módulo `src/graph/layout.py`, algoritmo de fuerzas Fruchterman-Reingold hecho a mano, usando el mismo generador con semilla). Así el dibujo es idéntico para la misma semilla.
- **`mapa.aristas`:** `a < b` siempre; `cluster` es `"corto"` o `"largo"`.
- **`entidades`:** solo las que existen al inicio. Los zombies que nacen de infecciones aparecen en `eventos`.
- **`mst`:** se calcula una sola vez con Prim sobre el grafo completo. Empieza en el nodo de menor id y desempata por `(peso, min(a, b), max(a, b))`.

---

## 3. Eventos

Lista ordenada por `(tick, seq)`. `seq` es un entero que empieza en 0, sube de a 1 y desempata eventos del mismo tick.

```json
[
  { "seq": 0, "tick": 1,  "tipo": "salida", "entidad": "Z1", "desde": 14, "hacia": 9, "llegada_tick": 9 },
  { "seq": 1, "tick": 9,  "tipo": "llegada", "entidad": "Z1", "nodo": 9 },
  { "seq": 2, "tick": 9,  "tipo": "fijacion", "zombie": "Z1", "objetivo": "S2", "nodo": 9 },
  { "seq": 3, "tick": 40, "tipo": "encuentro_ls", "nodo": 1, "zombie": "Z1", "superviviente": "S2", "resultado": "salvado", "extremidad": "pierna izquierda" },
  { "seq": 4, "tick": 40, "tipo": "salida", "entidad": "S2", "desde": 1, "hacia": 0, "llegada_tick": 49 },
  { "seq": 5, "tick": 49, "tipo": "a_salvo", "superviviente": "S2", "nodo": 0 },
  { "seq": 6, "tick": 62, "tipo": "infeccion", "nodo": 17, "zombie": "Z1", "victima": "S1", "nuevo_zombie": "Z2", "causa": "nodo_L" },
  { "seq": 7, "tick": 240, "tipo": "carronero", "superviviente": "S3", "nodo": 11, "final_id": 4 },
  { "seq": 8, "tick": 240, "tipo": "fin", "motivo": "limite_tiempo" }
]
```

| Tipo | Cuándo | Campos |
|---|---|---|
| `salida` | Una entidad parte hacia un nodo | `entidad`, `desde`, `hacia`, `llegada_tick` |
| `llegada` | Llega a un nodo **L o LS** | `entidad`, `nodo` |
| `fijacion` | El zombie fija (o refija) un objetivo | `zombie`, `objetivo`, `nodo` |
| `encuentro_ls` | Zombie y superviviente coinciden en una LS | `nodo`, `zombie`, `superviviente`, `resultado` (`"salvado"` o `"infectado"`), `extremidad` (texto o `null`) |
| `infeccion` | Un superviviente se convierte en zombie | `nodo`, `zombie` (quien infecta), `victima`, `nuevo_zombie`, `causa` (`"nodo_L"` o `"tirada_ls"`) |
| `a_salvo` | Un superviviente llega a la ZS | `superviviente`, `nodo` |
| `carronero` | Sigue activo al agotarse el tiempo | `superviviente`, `nodo`, `final_id` |
| `fin` | Termina la partida | `motivo` (`"sin_supervivientes"` o `"limite_tiempo"`) |

**Reglas de los eventos**
- Una llegada con encuentro emite primero `llegada`, y luego (mismo tick) `encuentro_ls` y/o `infeccion`.
- Una llegada a la ZS emite **solo** `a_salvo`, nunca `llegada`.
- Un superviviente salvado en una LS emite `encuentro_ls` y luego su `salida` hacia la ZS en ese mismo tick. Su `a_salvo` puede tener un tick **posterior** a `fin`: el frontend reproduce hasta el último evento.
- Una `salida` cuyo `llegada_tick` supera `limite_ticks` queda sin evento de llegada.
- No hay eventos para esperas ni reintentos.
- La posición de una entidad en viaje se interpola entre `tick` y `llegada_tick` a lo largo de la arista `desde`-`hacia`.

---

## 4. Resultados

```json
{
  "fin_tick": 240,
  "motivo_fin": "limite_tiempo",
  "zombie_inicial": {
    "id": "Z1",
    "capturas": [0, 1],
    "tiempo_promedio_caza_ticks": 31.5
  },
  "supervivientes": [
    {
      "id": "S1",
      "estado": "infectado",
      "tick_resolucion": 62,
      "tick_llegada_zs": null,
      "nodo_muerte": 17,
      "nodo_final": null,
      "final": null,
      "amputado": false,
      "extremidad": null,
      "encuentros_ls": [],
      "zombie_id": "Z2",
      "capturas": [2]
    }
  ],
  "capturas": [
    {
      "id": 0,
      "zombie": "Z1",
      "victima": "S1",
      "tick": 62,
      "nodo_muerte": 17,
      "persecucion": true,
      "nodo_fijacion": 9,
      "tick_fijacion": 9,
      "camino": [9, 12, 17],
      "distancia": 14,
      "tiempo_caza_ticks": 53
    }
  ],
  "encuentros_ls": [
    { "tick": 40, "nodo": 1, "zombie": "Z1", "superviviente": "S2", "resultado": "salvado", "extremidad": "pierna izquierda" }
  ]
}
```

**Superviviente**
- `estado`: `"sobrevivio"`, `"infectado"` o `"carronero"`.
- `tick_resolucion`: tick de llegada a la ZS, de infección o del límite de tiempo.
- `tick_llegada_zs`: solo si sobrevivió (incluso si fue rescatado en una LS y llegó después del fin).
- `nodo_muerte`: solo si fue infectado. `nodo_final`: solo si fue Carroñero (si iba en tránsito, su nodo de origen).
- `final`: si es Carroñero, `{ "id": 4, "texto": "...", "tono": "tragico" | "feliz" }`; si no, `null`.
- `amputado` y `extremidad`: solo si ganó el 50/50 en una LS.
- `encuentros_ls`: sus encuentros, con la misma forma que la lista global.
- `zombie_id` y `capturas`: si fue infectado, el id del zombie en que se convirtió y las capturas que hizo como zombie (habilitan `Ver Dash`, la "Conversión a Cazador"). Si no, `null` y `[]`.

**Captura**
- `persecucion`: `false` si el zombie no tenía fijada a la víctima (por ejemplo, el superviviente llegó a un zombie en reposo). En ese caso `nodo_fijacion`, `tick_fijacion`, `camino`, `distancia` y `tiempo_caza_ticks` son `null`.
- `camino`: **camino mínimo de Dijkstra entre `nodo_fijacion` y `nodo_muerte`, sobre el grafo sin la ZS**. No es el recorrido real del zombie.
- `distancia`: suma de los pesos de `camino`.
- `tiempo_caza_ticks`: `tick - tick_fijacion`.

**Zombie inicial**
- `capturas`: ids de las capturas que hizo Z1. `tiempo_promedio_caza_ticks`: promedio de las capturas con persecución, o `null` si no hay ninguna.
- Las capturas de zombies nacidos de infecciones **no** cuentan aquí: aparecen en la ficha del superviviente convertido.

---

## 5. Garantías (cada una debe tener test)
1. Misma `semilla` y mismos parámetros dan una respuesta **idéntica byte a byte**.
2. `eventos` está ordenado por `(tick, seq)` y `seq` es consecutivo desde 0.
3. Cada superviviente termina con exactamente un resultado: `a_salvo`, ser `victima` de una `infeccion`, o `carronero`.
4. La respuesta valida contra los modelos de `src/api/schemas.py`.
5. Todo `nodo` y `desde`/`hacia` existe en `mapa.nodos`; todo `desde`-`hacia` es una arista del mapa.
6. Con `modo_pruebas: true`, `limite_ticks` es 120.