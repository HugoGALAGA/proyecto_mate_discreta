discrete-math-project/
├── .github/
│   └── workflows/          # Integración Continua (GitHub Actions)
│       └── qa-pipeline.yml
├── docs/                   # Documentación y evidencias de QA
│   ├── test-plan.md
│   └── test-cases.md
├── src/                    # Código fuente del proyecto
│   └── __init__.py
├── tests/                  # Suite de Pruebas
│   ├── unit/               # Pruebas unitarias
│   ├── integration/        # Pruebas de integración
│   └── conftest.py         # Fixtures globales para Pytest
├── .gitignore              # Archivos a ignorar por Git
├── .pre-commit-config.yaml # Hooks de pre-commit para calidad de código
├── pyproject.toml          # Configuración de linters, formatters y pytest
├── README.md               # Documentación general del repositorio
└── requirements.txt        # Dependencias del proyecto