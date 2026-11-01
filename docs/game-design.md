# ZOMBIE SURVIVAL ENGINE — Documento maestro de diseño

Proyecto de Matemática Discreta (UFM). Estado: diseño cerrado, previo a implementación.
Lenguaje probable: Python. Interfaz: web.

---

## 0. Idea del juego

- Simulación de persecución sobre un **grafo ponderado**: un zombie inicial y 3 a 5 supervivientes se mueven solos por un mapa de 30 a 35 nodos.
- **No hay control directo del jugador.** El usuario configura la partida, la inicia y la observa. Toda la conducta es IA.
- Los supervivientes ganan al llegar a la **única Zona Segura (ZS)**. Los zombies ganan infectándolos. Si se agota el tiempo, los supervivientes restantes son **Carroñeros**.
- Contenido matemático: grafos ponderados, grado, conexidad, redes de mundo pequeño, Dijkstra (caminos mínimos), Prim (árbol de cobertura mínima, MST) y probabilidad (tirada 50/50).
- La simulación se calcula completa y rápido (reloj virtual) y genera un **registro de eventos**. La animación y las estadísticas se reproducen después sobre ese registro.

---

## 1. Glosario

| Término | Significado |
|---|---|
| S / Z | Superviviente / Zombie. Ids: S1, S2... y Z1, Z2... |
| ZS | Zona Segura. **Una sola** en todo el mapa. Es la meta. |
| LS | Nodo vecino directo de la ZS. Zona semi segura. |
| L | Nodo libre normal (todo lo que no es ZS ni LS). |
| Distancia | Suma de pesos del camino más corto (Dijkstra). Nunca es tiempo. |
| Cooldown | Espera obligatoria en un nodo antes de salir. |
| Tick | Unidad de tiempo interna = 0.5 s (ver sección 3). |
| Hoja | Nodo de grado 1 (callejón sin salida). |

---

## 2. Mapa

### 2.1 Forma
- 30 a 35 nodos (entero aleatorio en ese rango).
- Red de mundo pequeño (*small-world*): caminos cortos entre nodos y presencia de atajos.
- Grafo **conexo**, sin lazos (arista de un nodo a sí mismo) ni aristas repetidas.

### 2.2 Tipos de nodo
- **ZS:** exactamente 1. Grado 2 o 3. Nunca es hoja.
- **LS:** todos los vecinos de la ZS. Por tanto hay 2 o 3 LS (igual al grado de la ZS).
- **L:** el resto.

### 2.3 Grados
- L: grado máximo 4.
- LS: grado entre 2 y 3.
- ZS: grado entre 2 y 3.
- Hojas (grado 1): **máximo 4 en todo el mapa**, y solo pueden ser nodos L.
- No hay aristas LS–LS ni ZS–ZS.

### 2.4 Pesos
- Entero entre 1 y 10, asignado al azar a cada arista.
- Cluster corto: pesos 1 a 5. Cluster largo: pesos 6 a 10.
- Las aristas ZS–LS son **siempre cluster corto (1 a 5)**, para que desde cualquier LS se vea la ZS (visión de la ZS = 5).

### 2.5 Validaciones (todas obligatorias)
1. Cantidad de nodos entre 30 y 35.
2. Grafo conexo.
3. Exactamente 1 ZS con grado 2 o 3.
4. Cada LS con grado 2 o 3, sin aristas LS–LS, con arista a la ZS de peso 1 a 5.
5. Todo L con grado entre 1 y 4.
6. Hojas totales <= 4 y ninguna es ZS ni LS.
7. El grafo **sin la ZS** sigue conexo (si no, un zombie podría quedar encerrado lejos de todos).
8. Nodos de spawn válidos >= 6. Un nodo de spawn es un nodo **L** cuya distancia a la ZS (Dijkstra sobre el grafo completo) es >= 15.
9. Pesos enteros entre 1 y 10.

Si falla cualquiera, se **regenera** el mapa. Tope de 1000 intentos; si se alcanza, se lanza un error claro.
Opcional (solo informativo, no bloquea): reportar longitud media de camino y coeficiente de agrupamiento para justificar el carácter small-world.

### 2.6 Método de generación recomendado
1. Construir un grafo base tipo anillo con atajos aleatorios (estilo Watts-Strogatz) respetando el tope de grado 4.
2. Elegir como ZS un nodo con grado 2 o 3 cuyos vecinos tengan grado 2 o 3 y no sean vecinos entre sí.
3. Marcar sus vecinos como LS y el resto como L.
4. Asignar pesos y forzar 1 a 5 en las aristas ZS–LS.
5. Validar (2.5). Si falla, volver al paso 1.

### 2.7 Aleatoriedad
- Un único generador con **semilla inyectable**.
- Por defecto la semilla viene de entropía del sistema (hardware) y se **registra y muestra** en el dashboard.
- Con semilla fija, toda la partida (mapa, empates, tiradas, finales) es idéntica. Indispensable para Jenkins y Playwright.

---

## 3. Entidades y tiempos

| Dato | Zombie | Superviviente |
|---|---|---|
| Cantidad inicial | 1 | 3 a 5 (configurable) |
| Cooldown en nodo | 0.5 s (1 tick) | 1.5 s (3 ticks) |
| Viaje, arista corta (peso 1-5) | peso x 1 s (2 ticks por peso) | peso x 1.5 s (3 ticks por peso) |
| Viaje, arista larga (peso 6-10) | peso x 2 s (4 ticks por peso) | peso x 1.5 s (3 ticks por peso) |

- Ejemplos: Z en peso 5 = 5 s. Z en peso 10 = 20 s. S en peso 5 = 7.5 s. S en peso 10 = 15 s.
- **Tick = 0.5 s.** Recomendación de implementación: usar ticks enteros en todo el motor para evitar errores de coma flotante y desempates inestables.
- Spawn: cada entidad empieza en un nodo de spawn válido, **todos distintos**, elegidos al azar. Al inicio (tick 0) cada una arranca con su cooldown pendiente.

---

## 4. Motor de simulación (eventos discretos)

- Reloj virtual + **cola de prioridad** (heap) de eventos.
- Orden de eventos: (tick, número de secuencia). El número de secuencia crece cada vez que se agenda un evento y **desempata** eventos simultáneos.
- Tipos de evento:
  - `FIN_COOLDOWN(entidad)`: la entidad decide y sale.
  - `LLEGADA(entidad, nodo)`: la entidad llega a un nodo.
- Se procesa un evento por vez. Eventos con tick mayor al límite no se procesan.
- Límite de tiempo: **120 s (240 ticks)** en partida real, **60 s (120 ticks)** en pruebas. Configurable.
- Cada acción relevante se escribe en el **registro de eventos** (única fuente para animación y estadísticas).

---

## 5. Percepción

- Todas las distancias de visión se miden con Dijkstra sobre el **grafo completo**.
- **Posición percibida:** una entidad en reposo se ve en su nodo. Una entidad **en tránsito se ve en su nodo de origen** hasta que llega. Aplica igual a S y Z.
- Las entidades ya resueltas (a salvo o infectadas) no se perciben como supervivientes.

| Quién ve | Qué | Alcance (distancia total) |
|---|---|---|
| Zombie | Superviviente en nodo L | <= 15 |
| Zombie | Superviviente en nodo LS | <= 5 |
| Superviviente | Zombie | <= 10 |
| Superviviente | ZS | <= 5 |

---

## 6. Reglas de movimiento y ocupación

1. **Decisión solo en nodos:** al ocurrir `FIN_COOLDOWN`. Durante un viaje no se recalcula nada.
2. **Reserva al salir:** al partir, la entidad reserva el nodo destino.
3. **Superviviente:** no puede ir a un nodo L o LS ocupado o reservado por otro superviviente. La ZS admite cualquier cantidad.
4. **Zombie:** no puede ir a un nodo ocupado o reservado por otro zombie. **Puede** entrar a un nodo con superviviente (L o LS). **No puede entrar a la ZS.**
5. Un zombie **ignora** las reservas de supervivientes (puede llegar antes a un nodo que un superviviente reservó).
6. **Anti-vaivén:** al explorar, ninguna entidad vuelve al nodo del que acaba de venir, salvo que sea su única salida.
7. **Sin opciones válidas:** la entidad espera un cooldown completo en su nodo y reintenta.
8. En aristas no hay interacción: **cruzarse en una arista no infecta**. Justificación narrativa: en los nodos el superviviente descansa; en una arista se está moviendo y no se le puede atrapar.
9. Empates (en distancia o en candidatos): se resuelven **al azar** con el generador con semilla.

---

## 7. IA del Zombie

Al ocurrir `FIN_COOLDOWN` de un zombie en el nodo `u` en el tick `t`:

1. **Detectar:** lista de supervivientes activos visibles según la sección 5.
2. **Elegir objetivo:** para cada visible, calcular Dijkstra desde `u` sobre el **grafo sin la ZS**. Descartar los inalcanzables. Elegir el más cercano. Empate: al azar.
3. **Camino:** tomar el primer nodo del camino. Si ese nodo está ocupado o reservado por otro zombie, recalcular excluyendo los nodos bloqueados. Si no hay camino, esperar un cooldown y reintentar.
4. **Sin objetivo** (nadie visible o todos inalcanzables): ir al **vecino libre más cercano** (menor peso de arista), sin entrar a la ZS y con la regla anti-vaivén. Empate: al azar.
5. **Fijación de objetivo:** si el objetivo es nuevo (o se perdió y se retomó), se guarda `nodo_de_fijación = u` y `tick_de_fijación = t`. Si el objetivo se mantiene, se conservan.
6. Reservar el destino y agendar `LLEGADA` en `t + tiempo_de_viaje` (sección 3).

Los zombies creados por infección usan **exactamente la misma IA**.

---

## 8. IA del Superviviente

Al ocurrir `FIN_COOLDOWN` de un superviviente en el nodo `u`, en este orden de prioridad:

1. **ZS a la vista (distancia <= 5) y camino disponible:** ir hacia ella por el camino mínimo (Dijkstra sobre el grafo sin nodos bloqueados). Nodos bloqueados: ocupados o reservados por otro superviviente, o donde se percibe un zombie en reposo. Si no hay camino disponible, se pasa al punto 2 o 3.
2. **Zombie a la vista (distancia <= 10): huir.** Para cada vecino candidato `c` se calcula `puntaje(c) = distancia mínima desde c a los zombies visibles (en su posición percibida)`. Se elige el vecino con **mayor** puntaje. Empate: al azar.
3. **Sin zombie ni ZS a la vista: explorar.** Vecino candidato más cercano (menor peso de arista), con anti-vaivén. Empate: al azar.

Vecino candidato válido: no ocupado ni reservado por otro superviviente (la ZS siempre es válida) y sin zombie percibido en reposo. Sin candidatos: esperar un cooldown y reintentar.
Reservar el destino y agendar `LLEGADA` en `t + peso x 1.5 s`.

---

## 9. Llegadas y encuentros

Al ocurrir `LLEGADA` de una entidad al nodo `v`:

**A. Un superviviente llega a la ZS:** pasa a estado SOBREVIVIÓ y sale del juego. Se registra el tick.

**B. Encuentro en nodo L** (zombie y superviviente coinciden, llegue quien llegue):
- **Infección segura.** El superviviente pasa a INFECTADO y nace un nuevo zombie (Z2, Z3...) **en el mismo nodo**.
- Excepción temporal a la exclusividad de zombies: ambos (el que infectó y el nuevo) coexisten en `v`. Ambos reinician su ciclo: `FIN_COOLDOWN` en `t + 1 tick`. Luego se aplican las reglas normales (el segundo en reservar un destino igual no puede usarlo).
- El zombie que infectó recibe el crédito de la captura (si el superviviente llegó a un zombie en reposo, el crédito es del zombie en reposo).

**C. Encuentro en nodo LS** (zona semi segura): tirada 50/50 con el generador con semilla.
- **Se salva:** el superviviente sale **de inmediato** hacia la ZS, sin cooldown. En la arista no se le puede atrapar. Se marca como a salvo desde ese instante (SOBREVIVIÓ) y recibe la marca **AMPUTADO** con una extremidad al azar de `amputaciones.json`. Su hora de llegada a la ZS es `t + peso x 1.5 s`. El zombie se queda en la LS.
- **Muere:** se aplica lo mismo que en B (infección, Z nuevo en el mismo nodo, reinicio de ciclo).
- Se registra siempre el encuentro (nodo, tick, zombie, superviviente, resultado, extremidad si aplica).
- La LS no da otra ventaja: solo la visión reducida (5) y esta tirada.

**D. Llegada sin encuentro:** la entidad queda en reposo en `v` y se agenda `FIN_COOLDOWN` (1 tick para Z, 3 ticks para S).

**Captura sin persecución:** si el zombie no tenía fijado a ese superviviente (por ejemplo, el superviviente llegó a un zombie en reposo), la captura se registra sin `nodo_de_fijación` y sin camino de Dijkstra.

---

## 10. Fin de partida

La partida termina cuando ocurre **lo primero** de:
1. **No quedan supervivientes activos.** Activo = no está a salvo ni infectado. Un superviviente rescatado en la LS deja de ser activo en el instante de la tirada.
2. **Se alcanza el límite de tiempo** (sección 4).

Estados finales de un superviviente:
- **SOBREVIVIÓ:** llegó a la ZS (con marca AMPUTADO si pasó por la tirada de la LS).
- **INFECTADO:** murió (se volvió zombie).
- **CARROÑERO:** seguía activo al agotarse el tiempo. Recibe uno de **10 finales** (lista de datos, tono trágico o feliz, absurdos), elegido con la semilla.

---

## 11. Estadísticas y dashboard

La pantalla de resultados lista las entidades: **Z1 primero**, luego S1, S2...

**Ficha de Z1:**
- Supervivientes capturados.
- Tiempo total de cada captura (tick de captura) y tiempo de caza (captura menos fijación del objetivo).
- Tiempo promedio de caza.
- Botones: `Regresar al Menú` y `Ver Dash`.

**Ver Dash:**
- Se calcula **Prim una sola vez** al terminar la partida sobre el grafo completo (el MST no depende de la captura). Desempate determinista por id de nodo.
- Se dibuja el MST y, **encima, resaltado, el camino de Dijkstra** de la captura elegida (de `nodo_de_fijación` al nodo de la muerte).
- Selector para elegir qué captura inspeccionar. Capturas sin persecución muestran el MST con solo el nodo de la muerte marcado.

**Ficha de cada superviviente:**
- Estado: Sobrevivió, Infectado o Carroñero.
- Tiempo de supervivencia total (llegada a ZS, infección o límite de tiempo).
- Tiempo en llegar a la ZS (si aplica).
- Nodo exacto donde murió (si aplica). En Carroñero, el nodo donde estaba (el de origen si iba en tránsito).
- Carroñero: su final.
- Amputado: la extremidad perdida.
- Encuentros en LS y su resultado.
- Si fue infectado y luego, ya como zombie, capturó a otro: se habilita `Ver Dash` para esas capturas.

Siempre se muestra la **semilla** usada.

---

## 12. Menú y pantallas

1. **Menú principal:** Iniciar juego, Opciones, Sources.
2. **Opciones:** volumen, brillo, velocidad de reproducción (1x, 2x, 4x), cantidad de supervivientes (3 a 5) y semilla (aleatoria o fija). Se guardan en el navegador.
3. **Sources:** galería de imágenes, videos y gifs. Lee `assets/manifest.json` (título, tipo, archivo, créditos). Contenido por definir; agregarlo no requiere cambios de código.
4. **Partida:** reproducción animada del registro de eventos sobre el mapa, a la velocidad elegida.
5. **Dashboard** de resultados (sección 11).

---

## 13. Configuración (un solo archivo, `config.toml`)

| Parámetro | Valor |
|---|---|
| nodos_min / nodos_max | 30 / 35 |
| cantidad_zs | 1 |
| grado_max_L / grado_LS (min-max) / grado_ZS (min-max) | 4 / 2-3 / 2-3 |
| hojas_max | 4 |
| peso_corto / peso_largo | 1-5 / 6-10 |
| spawn_distancia_min / spawn_nodos_min | 15 / 6 |
| vision_zombie / vision_zombie_en_LS | 15 / 5 |
| vision_superviviente_zombie / vision_superviviente_zs | 10 / 5 |
| cooldown_zombie / cooldown_superviviente | 0.5 s / 1.5 s |
| factor_viaje_zombie_corto / largo | 1 / 2 |
| factor_viaje_superviviente | 1.5 |
| prob_salvarse_LS | 0.5 |
| supervivientes_min / max, zombies_iniciales | 3 / 5, 1 |
| limite_tiempo_partida / limite_tiempo_pruebas | 120 s / 60 s |
| semilla | vacío = entropía del sistema |
| intentos_max_generacion | 1000 |

Razón: afinar el balance sin tocar la lógica. Balance a vigilar: un superviviente necesita al menos 15 x 1.5 = 22.5 s para llegar a la ZS desde un spawn, y solo ve la ZS a <= 5, así que podrían salir muchos Carroñeros.

---

## 14. Stack y herramientas

- **Lenguaje:** Python.
- **Entorno:** WSL (Ubuntu/Linux) con terminal Fish Shell. Sin PowerShell.
- **Gestor de paquetes:** `uv`.
- **Visualización:** Graphify (`graphify . --code-only; graphify cluster-only .`).
- **Abrir en navegador de Windows desde WSL:** `cmd.exe /c start "" (wslpath -w (realpath graphify-out/graph.html))`.
- **Algoritmos:** Dijkstra y Prim implementados a mano con `heapq` (cola de prioridad de Python).
- **Pruebas:** pytest (propuesto) para unitarias y de simulación.
- **QA / CI:** Jenkins (orquestación) y Playwright (E2E de la interfaz con reporte HTML).
- **Servidor web:** ligero, en Python, sirviendo la interfaz estática (framework por definir con la estructura de código).

---

## 15. Estructura de carpetas (provisional, se ajusta con tu estructura de QA)

```
zombie-engine/
  pyproject.toml
  config.toml
  Jenkinsfile
  src/zombie_engine/
    rng.py
    config.py
    graph/   model.py  generator.py  validator.py  algorithms.py
    sim/     entities.py  events.py  engine.py
             ai_zombie.py  ai_survivor.py  rules.py
    stats/   recorder.py  summary.py
    data/    endings.json  amputaciones.json
    web/     server.py
             static/   (menu, opciones, sources, partida, dashboard)
             assets/   manifest.json
  tests/
    unit/    # grafo, Dijkstra, Prim, reglas
    sim/     # partidas con semilla fija, límite de 60 s
    e2e/     # Playwright
```

---

## 16. Plan de pruebas (qué debe verificarse)

- **Mapa:** con N semillas, todo mapa generado cumple la sección 2.5. Falla controlada tras 1000 intentos.
- **Dijkstra:** distancias correctas en grafos pequeños hechos a mano; exclusión de la ZS.
- **Prim:** peso total mínimo y n-1 aristas en grafos conocidos.
- **Reglas:** reserva al salir, exclusividad de S y de Z, infección en L, tirada en LS (con semilla fija se prueban ambos resultados), cruce en arista sin infección, anti-vaivén, espera por falta de vecinos.
- **Visión:** límites exactos (15, 10, 5) y visión reducida en LS.
- **Motor:** desempate por número de secuencia, límite de tiempo, fin por cero supervivientes activos.
- **Determinismo:** misma semilla produce el mismo registro de eventos, byte a byte.
- **Estadísticas:** estados, tiempos, Carroñero con final, Amputado, conversión a cazador.
- **E2E (Playwright):** menú, opciones persistidas, galería Sources, partida con semilla fija, dashboard y `Ver Dash`.

---

## 17. Casos borde resueltos

| Situación | Resolución |
|---|---|
| Dos entidades reservan el mismo nodo en el mismo tick | Gana la que tenga menor número de secuencia; la otra elige otro o espera |
| El objetivo se movió y el zombie llega a un nodo vacío | Cooldown normal y nueva decisión |
| Objetivo en la ZS | No se persigue (la ZS es inaccesible para zombies) |
| Zombie llega a un nodo reservado por un superviviente en tránsito | Entra (ignora reservas de S); cuando el superviviente llega, hay encuentro |
| Superviviente llega a un nodo con zombie en reposo | Misma regla que si llegara el zombie (infección en L, tirada en LS) |
| Dos zombies tras infección quieren la misma arista | El segundo en reservar no puede usarla; elige otra o espera |
| Se acaba el tiempo con entidades en tránsito | No se procesan llegadas posteriores al límite; los S activos son Carroñeros |
| Superviviente rescatado en LS y el tiempo se agota en su viaje a la ZS | Sigue contando como SOBREVIVIÓ |
| Superviviente atrapado en una hoja con un zombie acercándose | Sin candidatos válidos, espera y reintenta |

---

## 18. Supuestos añadidos que debes validar

1. Las entidades arrancan en el tick 0 con su cooldown pendiente.
2. La visión se mide en el grafo completo; el camino del zombie, en el grafo sin la ZS.
3. Al huir con varios zombies visibles, se maximiza la distancia mínima a cualquiera de ellos.
4. Un superviviente evita nodos donde percibe un zombie en reposo.
5. Tiempo de caza = tick de captura menos tick de fijación; tiempo total = tick de captura.
6. Sin persecución previa, la captura se registra sin camino de Dijkstra.
7. LS con grado mínimo 2, sin aristas LS–LS y arista ZS–LS de peso 1 a 5.
8. El carácter small-world se reporta con métricas pero no bloquea la generación (el tope de grado 4 limita el agrupamiento).

---

## 19. Pendientes

- Redactar los **10 finales de Carroñero** y la lista de **amputaciones** (`data/`).
- Contenido de **Sources** (imágenes, videos, gifs).
- Contexto final para Gemini.