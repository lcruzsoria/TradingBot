"""Traduce los errores técnicos de carga en una explicación y una acción concreta."""
from __future__ import annotations


def explain_error(error: str) -> str:
    low = error.lower()
    if "no existe en este broker" in low or "no disponible" in low:
        return ("Ese nombre no existe tal cual en tu broker. Pulsa «Editar» en Mercados, quita el símbolo y "
                "añade el que aparezca al buscarlo (por ejemplo «nasdaq» o «dow»).")
    if "sin velas" in low:
        return ("El símbolo existe, pero MT5 aún no tiene su historial. Abre ese gráfico en MT5 y desplázate "
                "hacia atrás un rato para que lo descargue; luego pulsa de nuevo el mercado.")
    if "call failed" in low or "initialize" in low or "ipc" in low or "no hay conexión" in low:
        return ("MT5 no responde. Comprueba que está abierto con la cuenta iniciada y con permisos normales "
                "(no administrador). Si sigue igual, ciérralo, ábrelo de nuevo y reinicia el bot.")
    if "cuenta" in low and "perfil" in low:
        return "El terminal está en otra cuenta distinta a la del perfil. Cambia de cuenta en MT5."
    return "Mira el Registro para ver el detalle. Para reintentar, pulsa de nuevo el mercado o un timeframe."
