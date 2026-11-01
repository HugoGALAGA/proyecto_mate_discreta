"""Genera CONTEXT.md con el árbol y el contenido relevante del proyecto.

Uso (desde la raíz del proyecto):
    python generar_contexto.py
"""

from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ / "CONTEXT.md"

# Carpetas que NO se recorren (pesadas, temporales o sin valor de negocio)
CARPETAS_IGNORADAS = {
    ".git",
    ".github",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "htmlcov",
    "graphify-out",
    "node_modules",
    ".mypy_cache",
    "pre_diseño",  # Borradores de interfaz
}

# Archivos específicos que NO se incluyen en la lectura de contexto
ARCHIVOS_IGNORADOS = {
    "uv.lock",
    ".coverage",
    "CONTEXT.md",
    "generar_contexto.py",
    "nodesource_setup.sh",  # Script masivo de setup de NodeSource
    "setup_entorno.sh",  # Script de provisionamiento local
}

# Extensiones cuyo contenido SÍ se incluye en la sección de Contenido
EXTENSIONES = {
    # Backend / Config
    ".py",
    ".toml",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    # Frontend / Web
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".html",
    ".css",
    ".json",
    # Documentación
    ".md",
    ".txt",
}

# Archivos especiales sin extensión a incluir
NOMBRES_EXTRA = {".gitignore", "Jenkinsfile", "Dockerfile"}

# Máximo de caracteres por archivo
# (para evitar desbordar el contexto si hay archivos enormes)
MAX_CARACTERES = 15_000


def es_ignorado(ruta: Path) -> bool:
    return any(parte in CARPETAS_IGNORADAS for parte in ruta.parts)


def listar_archivos() -> list[Path]:
    archivos = []
    for ruta in sorted(RAIZ.rglob("*")):
        rel = ruta.relative_to(RAIZ)
        if not ruta.is_file() or es_ignorado(rel):
            continue
        if rel.name not in ARCHIVOS_IGNORADOS:
            archivos.append(rel)
    return archivos


def construir_arbol(archivos: list[Path]) -> str:
    arbol: dict = {}
    for rel in archivos:
        nodo = arbol
        for parte in rel.parts:
            nodo = nodo.setdefault(parte, {})

    lineas = [f"{RAIZ.name}/"]

    def recorrer(nodo: dict, prefijo: str) -> None:
        items = sorted(nodo.items(), key=lambda kv: (not kv[1], kv[0].lower()))
        for i, (nombre, hijos) in enumerate(items):
            ultimo = i == len(items) - 1
            conector = "└── " if ultimo else "├── "
            lineas.append(prefijo + conector + nombre + ("/" if hijos else ""))
            if hijos:
                recorrer(hijos, prefijo + ("    " if ultimo else "│   "))

    recorrer(arbol, "")
    return "\n".join(lineas)


def main() -> None:
    archivos = listar_archivos()
    partes = [
        f"# Contexto del proyecto: {RAIZ.name}\n",
        "## Estructura del Proyecto\n",
        "```\n" + construir_arbol(archivos) + "\n```\n",
        "## Contenido de Archivos Relevantes\n",
    ]

    for rel in archivos:
        if rel.suffix not in EXTENSIONES and rel.name not in NOMBRES_EXTRA:
            continue
        try:
            texto = (RAIZ / rel).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        if len(texto) > MAX_CARACTERES:
            texto = texto[:MAX_CARACTERES] + "\n... [recortado por tamaño]"

        if not texto.strip():
            partes.append(f"### {rel.as_posix()}\n\n(archivo vacío)\n")
            continue

        # Evita romper bloques de código Markdown si el archivo trae ```
        cerca = "```"
        while cerca in texto:
            cerca += "`"

        lenguaje = rel.suffix.lstrip(".") or "text"
        partes.append(f"### {rel.as_posix()}\n\n{cerca}{lenguaje}\n{texto}\n{cerca}\n")

    resultado = "\n".join(partes)
    SALIDA.write_text(resultado, encoding="utf-8")
    caracteres = len(resultado)
    tokens = caracteres // 4
    print(
        f"✅ Contexto limpio generado: {SALIDA.name}"
        f"({caracteres:,} caracteres, ~{tokens:,} tokens estimación)"
    )


if __name__ == "__main__":
    main()
