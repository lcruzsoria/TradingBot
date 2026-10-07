"""Skills disponibles: una carpeta por skill, que se registra automáticamente.

Cada skill vive en su propia carpeta (por ejemplo `skills/bias/`) con, como mínimo, un `skill.py` que define la clase
con `@register_skill`. En la misma carpeta van los módulos propios de esa skill (motor, reglas, cálculos...).
Las carpetas que empiezan por "_" se ignoran (por ejemplo, la plantilla `_plantilla/`).
"""
import importlib
import pkgutil

for _mod in pkgutil.iter_modules(__path__):
    if _mod.ispkg and not _mod.name.startswith("_"):
        importlib.import_module(f"{__name__}.{_mod.name}.skill")
