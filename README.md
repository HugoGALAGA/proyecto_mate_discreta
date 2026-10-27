# 🧮 Discrete Mathematics Engine & QA Framework

[![QA Pipeline](https://github.com/HugoGALAGA/proyecto_mate_discreta/actions/workflows/qa-pipeline.yml/badge.svg)](https://github.com/HugoGALAGA/proyecto_mate_discreta/actions/workflows/qa-pipeline.yml)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)
![Coverage: >80%](https://img.shields.io/badge/coverage-%3E80%25-brightgreen)

Repositorio base para la implementación de algoritmos de **Matemática Discreta**, estructurado y diseñado bajo la metodología **Shift-Left QA**, prácticas modernas de **Integración Continua (CI/CD)** y principios internacionales **ISTQB**.

---

## 📐 1. Propósito e Ideas Clave del Proyecto

Este repositorio aprovecha el desarrollo de un proyecto académico de Matemática Discreta (grafos, relaciones, lógica, autómatas) como un escenario real para aplicar conceptos avanzados de **Ingeniería de Software y Calidad (QA)**:

- **Estrategia Shift-Left:** Detección de errores y bugs en las etapas más tempranas del ciclo de desarrollo (localmente antes del commit y en cada push).
- **Quality Gates Automáticos:** Bloqueo automático de código mediante análisis estático y umbrales de cobertura dinámica antes de permitir fusiones en la rama principal.
- **TDD (Test-Driven Development):** Enfoque *Red-Green-Refactor* para el diseño de algoritmos matemáticos comprobables.
- **Fast Tooling (Stack en Rust):** Uso de `uv` como gestor de entorno/paquetes ultrarrápido y `Ruff` como linter estático de alta velocidad.

---

## 🛠️ 2. Estructura del Repositorio

La arquitectura del proyecto sigue una separación clara entre el código fuente, la suite de pruebas automatizadas y las herramientas de automatización de CI:

```text
proyecto_mate_discreta/
├── .github/
│   └── workflows/
│       └── qa-pipeline.yml    # Pipeline de CI/CD (GitHub Actions)
├── docs/                      # Documentación del proyecto y planes de prueba
│   └── .gitkeep
├── src/                       # Código fuente del núcleo matemático
│   ├── __init__.py
│   └── core.py                # Algoritmos base y estructuras de datos
├── tests/                     # Suite de pruebas automatizadas
│   ├── integration/           # Pruebas de integración / API (Gray-box)
│   │   └── .gitkeep
│   ├── unit/                  # Pruebas unitarias y basados en propiedades (White-box)
│   │   └── test_core.py
│   ├── __init__.py
│   └── conftest.py            # Fixtures globales de Pytest
├── .gitignore                 # Exclusión de archivos binarios y caché local
├── .pre-commit-config.yaml    # Gate de calidad estática previa a commit local
├── pyproject.toml             # Configuración centralizada de herramientas (Ruff, Pytest, Coverage)
├── requirements.txt           # Dependencias del proyecto
└── README.md                  # Documentación principal