"""Skills disponibles. Cualquier módulo nuevo en esta carpeta se registra automáticamente.

Los ficheros que empiezan por "_" se ignoran (por ejemplo, la plantilla `_plantilla.py`).
"""
import importlib
import pkgutil

for _mod in pkgutil.iter_modules(__path__):
    if not _mod.name.startswith("_"):
        importlib.import_module(f"{__name__}.{_mod.name}")
