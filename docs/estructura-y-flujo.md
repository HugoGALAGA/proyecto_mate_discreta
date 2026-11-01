# Estructura del repositorio y flujo de trabajo

Documento para quien programe en este repo (humano o Gemini). Se lee junto con **`docs/game-design.md`**, que es la fuente de verdad de las reglas del juego. Este documento define dónde va cada cosa, cómo se escribe y prueba el código y cómo se trabaja con Git.

Repositorio: github.com/HugoGALAGA/proyecto_mate_discreta

---

## 1. Resumen

**Zombie Survival Engine** (Matemática Discreta, UFM): simulación de persecución zombie vs supervivientes sobre un grafo ponderado.

- **Python** calcula toda la simulación (mapa, IA, eventos, estadísticas) y genera un registro de eventos.
- **FastAPI** expone ese resultado como JSON.
- **React** lo reproduce como animación y muestra el dashboard.
- Todo se prueba en tres niveles (unit, integration, e2e) y pasa por un gate de calidad en GitHub Actions y un pipeline completo en Jenkins.

---

## 2. Stack y versiones

| Pieza | Herramienta |
|---|---|
| Lenguaje principal | Python 3.11 (`.python-version`) |
| Gestor de entorno y dependencias | `uv` (`pyproject.toml` + `uv.lock`) |
| Servidor | FastAPI + uvicorn |
| Frontend | React 18 + Vite 5, JavaScript (sin TypeScript) |
| Lint y formato Python | ruff (`line-length = 88`, reglas E, F, I, W, destino py311) |
| Lint frontend | ESLint 9 (configuración plana + `eslint-plugin-react`) |
| Pruebas Python | pytest, pytest-cov, pytest-html, hypothesis, httpx |
| Pruebas E2E | pytest-playwright (Chromium) |
| Node.js | 24 |
| CI rápido | GitHub Actions |
| CI completo | Jenkins (en WSL) |
| Entorno de desarrollo | Windows + WSL (Ubuntu) con terminal Fish |

- Go y Rust **no se usan**. Solo se considerarían ante una necesidad puntual acordada.
- Dijkstra y Prim se implementan **a mano** con `heapq`, sin librerías de grafos.
- El repo vive en una ruta de Windows (`/mnt/c/...`) y no se puede mover. Instalar y correr pruebas es más lento de lo normal; por eso los tiempos de espera de los E2E son holgados.

---

## 3. Estructura de carpetas

Leyenda: ✅ ya existe · 🔲 por crear (definido en `docs/game-design.md`).

```
proyecto_mate_discreta/
├── .github/workflows/qa-pipeline.yml   ✅ GitHub Actions (gate rápido)
├── Jenkinsfile                         ✅ pipeline completo con E2E
├── config.toml                         ✅ TODOS los parámetros del juego (juego, layout y API)
├── pyproject.toml                      ✅ dependencias y herramientas
├── uv.lock                             ✅ versiones exactas (se commitea)
├── .python-version                     ✅ 3.11
├── .pre-commit-config.yaml             ✅ ruff + ruff-format antes de commit
├── generar_contexto.py                 ✅ genera CONTEXT.md local (ignorado por git)
├── README.md                           ✅ (desactualizado, por renovar)
├── docs/
│   ├── contrato-api.md                 ✅ formato JSON de la API (v1)       
│   ├── game-design.md                  ✅ reglas completas del juego
│   ├── estructura-y-flujo.md           ✅ este documento
│   ├── test-plan.md                    🔲 estrategia de pruebas (vacío)
│   ├── test-cases.md                   🔲 casos de prueba (vacío)
│   └── img/
├── pre_diseño/proyecto.pdf             ✅ idea original (histórico, NO vigente)
├── src/                                # paquete Python (se importa como `src`)
│   ├── __init__.py
│   ├── config.py                       ✅ cargar_config() lee config.toml
│   ├── rng.py                          🔲 generador único con semilla inyectable
│   ├── graph/                          ✅ (vacío)
│   │   ├── model.py                    🔲 Node, Edge, Graph
│   │   ├── layout.py                   🔲 posiciones (x, y) por fuerzas, usa rng   
│   │   ├── generator.py                🔲 genera el mapa y regenera si falla
│   │   ├── validator.py                🔲 validaciones del mapa (sección 2.5)
│   │   └── algorithms.py               🔲 Dijkstra y Prim
│   ├── sim/                            ✅ (vacío)
│   │   ├── entities.py                 🔲
│   │   ├── events.py                   🔲 cola de prioridad (tick, secuencia)
│   │   ├── rules.py                    🔲 ocupación, reserva, infección, 50/50
│   │   ├── ai_zombie.py                🔲
│   │   ├── ai_survivor.py              🔲
│   │   └── engine.py                   🔲 bucle de eventos
│   ├── stats/                          ✅ (vacío)
│   │   ├── recorder.py                 🔲 registro de eventos
│   │   └── summary.py                  🔲 estadísticas por entidad, MST con Prim
│   ├── data/                           ✅ (vacío)
│   │   ├── endings.json                🔲 10 finales de Carroñero
│   │   └── amputaciones.json           🔲 extremidades
│   └── api/
│       ├── app.py                      ✅ crear_app(); /api/health; sirve frontend/dist
│       └── schemas.py                  🔲 modelos Pydantic del contrato
├── frontend/                           # React + Vite
│   ├── package.json, package-lock.json, vite.config.js, eslint.config.js, index.html
│   ├── public/assets/manifest.json     ✅ galería de Sources (hoy vacía)
│   ├── src/main.jsx, App.jsx           ✅ menú de marcador
│   └── src/                            🔲 pantallas: Menu, Options, Sources, Game, Dashboard
└── tests/
    ├── conftest.py                     ✅
    ├── unit/                           ✅ test_config.py
    ├── integration/                    ✅ test_api.py
    └── e2e/                            ✅ conftest.py (servidor real), test_menu.py
```

**Carpetas generadas y no versionadas** (están en `.gitignore`): `.venv/`, `node_modules/`, `frontend/dist/`, `htmlcov/`, `.coverage`, `.pytest_cache/`, `.ruff_cache/`, `.hypothesis/`, `playwright-report/`, `test-results/`, `reports/`, `graphify-out/`, `CONTEXT*.md`.

---

## 4. Cómo se conectan las piezas

```
config.toml ──► src/config.py ──► src/graph, src/sim, src/stats
                                        │
                          (simulación completa, reloj virtual)
                                        ▼
                         registro de eventos + estadísticas (JSON)
                                        │
                  src/api/app.py  (POST /api/simulate: 🔲 por definir)
                                        │
                                        ▼
         frontend (React): reproduce el registro a la velocidad elegida
```

- La simulación **no** corre en tiempo real: se calcula completa y rápido, y la interfaz **reproduce** el resultado.
- En producción y en E2E, FastAPI sirve `frontend/dist/` (un solo servidor, un solo puerto).
- En desarrollo, Vite corre aparte y redirige `/api` a `http://127.0.0.1:8000`.
- Hoy solo existe `GET /api/health`. 
- El contrato (`GET /api/parametros`, `POST /api/simulate`) está definido en `docs/contrato-api.md` y es **obligatorio**: se implementa con modelos Pydantic en `src/api/schemas.py`. Hoy solo existe `GET /api/health`.

---

## 5. Reglas del código

### Reglas generales
- **Fuente de verdad del juego:** `docs/game-design.md`. Si algo es ambiguo o hay un supuesto sin validar (sección 18), **se pregunta**; no se decide por cuenta propia.
- Nombres de funciones, variables y comentarios en **español**, como el código actual (`cargar_config`, `crear_app`).
- Comentarios mínimos: solo donde la intención no sea obvia.
- Ninguna dependencia nueva sin acordarla. Si se acuerda, se agrega a `pyproject.toml` y se corre `uv lock`.
- Los nombres de los parámetros de `config.toml` son un contrato: no se renombran sin avisar.
- El formato JSON vive en `docs/contrato-api.md`. Un cambio de formato se aprueba primero en ese documento y después en el código.

### Python
- Pasa `ruff check .` y `ruff format --check .` sin cambios.
- Imports ordenados (regla `I`); líneas de máximo 88 caracteres.
- Tipos en las firmas de funciones públicas.
- `src/graph` y `src/sim` son **lógica pura**: sin lectura de archivos, sin red, sin `print`, sin reloj del sistema.
- **Un solo generador aleatorio**, recibido por parámetro (semilla inyectable). Prohibido usar `random` global o `time` para decisiones del juego.
- El tiempo es **entero, en ticks** (1 tick = 0.5 s). Prohibido usar floats para el reloj de la simulación.
- **Ningún número del juego va escrito en el código**: todo viene de `config.toml`.
- **Determinismo:** misma semilla, mismo registro de eventos, byte a byte.
- Cada subcarpeta de `src/` tiene su `__init__.py`.
- Las posiciones del mapa las calcula `graph/layout.py` con el generador con semilla; el frontend nunca las inventa.

### Frontend
- JavaScript con componentes de función y hooks. Sin TypeScript.
- Pasa `npm run lint` sin errores y `npm run build` sin fallos.
- El mapa se dibuja con **SVG**; sin librerías de grafos ni de animación sin acordarlas.
- Datos del servidor con `fetch("/api/...")`.
- Volumen, brillo, velocidad de reproducción, cantidad de supervivientes y semilla viven en el navegador (`localStorage`) y se envían a la API cuando corresponde.
- Textos de la interfaz en español.

---

## 6. Pruebas

| Nivel | Carpeta | Marcador | Qué cubre |
|---|---|---|---|
| Unit | `tests/unit/` | `unit` (y `property` si usa Hypothesis) | Grafo, Dijkstra, Prim, reglas, configuración |
| Integration | `tests/integration/` | `integration` | Partidas completas con semilla fija y límite de 60 s; API con `TestClient` |
| E2E | `tests/e2e/` | `e2e` | Navegador real con Playwright sobre el servidor real |

**Normas**
- Cada archivo de test declara su nivel: `pytestmark = pytest.mark.unit` (o `integration`, `e2e`). Se usa `--strict-markers`: un marcador no declarado en `pyproject.toml` da error.
- Los nombres de archivo de test son **únicos en todo `tests/`** (`tests/unit` y `tests/integration` no tienen `__init__.py`).
- Cada módulo nuevo llega **con sus tests** (enfoque TDD: rojo, verde, refactor).
- **Hypothesis** para propiedades: todo mapa generado cumple las validaciones, Dijkstra coincide con una búsqueda por fuerza bruta, Prim devuelve n-1 aristas de peso mínimo, misma semilla da el mismo resultado.
- Las partidas de prueba usan semilla fija y `limite_pruebas = 60`.
- **Cobertura mínima: 80%** (con ramas), exigida solo en los comandos de CI y Jenkins, **no** en `addopts` (así se puede correr un archivo suelto).
- Los E2E se excluyen por defecto (`addopts = -m 'not e2e'`). El fixture `servidor` levanta uvicorn en un puerto libre y espera hasta 2 minutos; `base_url` apunta a ese servidor. Requieren `frontend/dist/` compilado.

**Cobertura de cada nivel (lo que debe existir al final)**
- Mapa, algoritmos, reglas, visión, motor, estadísticas y determinismo: ver sección 16 de `docs/game-design.md`.
- E2E: menú, opciones persistidas, galería Sources, partida con semilla fija, dashboard y `Ver Dash`.

---

## 7. Comandos de uso diario

Se ejecutan desde la raíz del repo, en Fish.

```
# Instalación (una vez, o tras cambiar dependencias)
uv sync --group dev
cd frontend; npm install; cd ..

# Calidad
uv run ruff check .
uv run ruff format .
cd frontend; npm run lint; cd ..

# Pruebas (unit + integration; excluye e2e)
uv run pytest
uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=80

# Desarrollo (dos terminales)
uv run uvicorn src.api.app:app --reload --port 8000
cd frontend; npm run dev

# E2E
cd frontend; npm run build; cd ..
uv run playwright install chromium            # una sola vez
sudo .venv/bin/playwright install-deps chromium   # una sola vez
uv run pytest tests/e2e -m e2e
```

Nota para Fish: no soporta bloques `<<EOF`. Para crear archivos con varias líneas se usa un editor o un script `.sh` ejecutado con `bash`.

---

## 8. Integración continua

### GitHub Actions: gate rápido
Archivo `.github/workflows/qa-pipeline.yml`. Corre en `push` a `main` y `dev`, y en Pull Requests hacia `main`. **No** ejecuta E2E.

- **`python-gate`:** `uv sync --group dev`, `ruff check .`, `pytest -m "not e2e"` con cobertura mínima de 80% y subida del reporte `htmlcov`.
- **`frontend-gate`:** Node 24, `npm ci`, `npm run lint`, `npm run build`.

### Jenkins: pipeline completo
Archivo `Jenkinsfile` (declarativo, corre en WSL). Disparo por revisión periódica del repo (`pollSCM`) o a mano; un Jenkins local no recibe avisos de GitHub sin un túnel. Tope de 20 minutos.

Etapas: instalar dependencias (`uv sync`, `npm ci`, `playwright install chromium`) → lint (ruff y ESLint en paralelo) → unit + integration con cobertura ≥ 80% y JUnit → build de React → E2E con Playwright (reporte HTML con pytest-html, JUnit, capturas y trazas si falla). Al terminar archiva `htmlcov`, `playwright-report` y `test-results`, y publica los JUnit.

Requisitos en la máquina de Jenkins: `uv` y Node 24 en el PATH del usuario `jenkins`, JDK para Jenkins, y las librerías de sistema de Chromium. La instancia de Jenkins se configura aparte (**pendiente**).

---

## 9. Flujo de trabajo con Git

**Ramas**
- `main`: estable. Solo recibe cambios por Pull Request.
- `dev`: trabajo diario. **No se borra** después de fusionar.

**Ciclo de trabajo**
1. `git switch dev` y `git pull`.
2. Programar con tests (TDD). Probar en local: `ruff`, `pytest`, y `npm run lint` si se tocó el frontend.
3. `git add -A`, `git status --short` (revisar que no se cuele nada ignorado) y `git commit`.
4. `git push` a `dev`: GitHub Actions corre solo.
5. Con todo en verde, abrir un **Pull Request de `dev` a `main`**.
6. Esperar los checks del PR; si todo está en verde, **Merge pull request** (sin pulsar *Delete branch*).
7. Sincronizar: `git switch main`, `git pull`, `git switch dev`, `git merge main`.

**Mensajes de commit:** prefijo + descripción corta, en español: `feat:` (funcionalidad), `fix:` (corrección), `test:` (pruebas), `docs:` (documentación), `chore:` (entorno y configuración), `refactor:`.

**Pre-commit:** ruff y ruff-format corren antes de cada commit si el hook está instalado (`uv run pre-commit install`, una vez). Si modifican archivos, el commit se cancela: repetir `git add -A` y `git commit`.

---

## 10. Orden de implementación recomendado

Cada paso termina con tests en verde y un commit.

1. **`rng.py`:** generador con semilla inyectable. Tests de determinismo.
2. **`graph/model.py` y `graph/algorithms.py`:** estructuras, Dijkstra, Prim. Tests con grafos hechos a mano y propiedades.
3. **`graph/validator.py` y `graph/generator.py`:** todas las validaciones y regeneración. Propiedad: todo mapa generado es válido.
4. **`sim/entities.py` y `sim/events.py`:** entidades, estados y cola de prioridad con desempate.
5. **`sim/rules.py`:** ocupación, reserva, infección, tirada 50/50 y Amputado.
6. **`sim/ai_zombie.py` y `sim/ai_survivor.py`:** decisiones de cada IA.
7. **`sim/engine.py` y `stats/`:** bucle de eventos, límite de tiempo, registro y estadísticas (incluido Prim al final).
8. **`data/`:** 10 finales de Carroñero y lista de amputaciones.
9. **Contrato JSON y `POST /api/simulate`.**
10. **Frontend:** menú, opciones, Sources, partida (animación), dashboard.
11. **E2E** de cada flujo y revisión del balance con la configuración.
12. api/schemas.py, GET /api/parametros, POST /api/simulate y tests del contrato

---

## 11. Cómo pedirle trabajo a Gemini

Plantilla recomendada, un módulo por vez:

```
Contexto: lee docs/game-design.md, docs/estructura-y-flujo.md y docs/contrato-api.md.
Tarea: implementa <módulo> (paso N de la sección 10).
Contrato: <firmas de funciones y estructuras de datos esperadas>.
Reglas: sigue la sección 5 del documento de estructura; sin dependencias nuevas.
Entrega: primero los tests (unit con marcador), luego el código.
Si algo del diseño es ambiguo, pregunta antes de decidir.
```

---

## 12. Estado actual y pendientes

**Hecho**
- Entorno completo (Python 3.11, uv, FastAPI, React + Vite), CI en GitHub Actions en verde y flujo `dev` → `main` probado.
- Un test por nivel funcionando, incluido un E2E real con Playwright.
- Contrato JSON v1 definido (docs/contrato-api.md).

**Pendiente**
- Toda la lógica del juego (sección 10).
- Implementar schemas.py y los endpoints del contrato.
- Llenar `docs/test-plan.md` y `docs/test-cases.md` a medida que se escriben las pruebas.
- Configurar la instancia de Jenkins.
- Actualizar `README.md` y la versión de ruff en `.pre-commit-config.yaml`.
- Contenido de Sources (imágenes, videos y gifs).
- Los 8 supuestos de la sección 18 de `docs/game-design.md` siguen por validar.