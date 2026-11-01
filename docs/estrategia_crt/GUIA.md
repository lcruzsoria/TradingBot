# CRT (Candle Range Theory): guía de la estrategia

Estado: **backtest hecho en NAS100 y forex con la regla del FVG de MTF corregida (02/11/2026): ninguna de las combinaciones pasa los criterios** (NAS100 M5/M3 y M1, EURUSD/GBPUSD M5/M3, con y sin esperar al cierre de C2). Resultados en [RESULTADOS.md](RESULTADOS.md) y los RESULTADOS_*.md; script en `scripts/backtest_crt.py`. Ejemplos dibujados paso a paso en `operacion_2025-07-30/` (corto) y `operacion_2026-09-17/` (largo).

Dibujos: [reglas_crt.png](reglas_crt.png) (reglas completas) y [criterios_htf_mtf.png](criterios_htf_mtf.png) (los dos criterios previos). Las reglas de abajo son las mismas que muestran los dibujos.

## 1. Idea

Una vela de timeframe alto (HTF) marca un rango. El precio barre uno de sus extremos (liquidez externa), llega además a un desequilibrio que ya existía en un timeframe medio (liquidez interna) y después se da la vuelta. En un timeframe bajo se busca la confirmación del giro y se entra.

Se describe el corto (barrido de un máximo). El largo es el espejo exacto.

## 2. Timeframes y mercado

| Papel | Índices | Forex |
|---|---|---|
| HTF (sweep) | H3 | H4 |
| MTF (FVG de confirmación) | M15, M30 o H1 | M15, M30 o H1 |
| LTF (iFVG, CISD y entrada) | M5 o M3 | M5 o M3 |

- Primer mercado: **NAS100**. Forex en una segunda fase.
- Cierre de sesión en índices: **18:00 NY**.
- Perfil aparte en el bot, con su propio skill `crt`.

## 3. Reglas

Todas son obligatorias y se evalúan en este orden. Si falta una, no hay trade.

### Criterio 1 · Sweep en HTF (liquidez externa)
- Una vela HTF (C2) supera el máximo (o mínimo) de la vela anterior (C1) y **cierra dentro del rango de C1**.
- Si C2 cierra fuera, es una rotura y no hay patrón.
- Si C2 supera los dos extremos de C1, no hay sesgo y no se opera.
- Máximo barrido → **corto**. Mínimo barrido → **largo**.

### Criterio 2 · FVG tocado en MTF (liquidez interna)
- El extremo del sweep (el máximo o mínimo de C2) toca un **FVG de M15, M30 o H1 ya formado** antes del sweep.
- **Corto:** un FVG **bajista**, creado antes en el desarrollo del precio (en la bajada), que queda **entero por encima del máximo de C1**. Eso asegura una tendencia bajista (el FVG está más arriba que C1) y que el sweep ha tomado liquidez interna.
- **Largo:** el espejo: un FVG **alcista** que queda entero **por debajo del mínimo de C1**.
- Un FVG cuyo borde coincide con el extremo de C1 (formado dentro de C1) **no vale**: tiene que estar más allá. (Corrección del 02/11/2026; antes se aceptaba. Con NAS100 quita el 7 % de los setups.)
- Dibujo de la regla: [regla_fvg_mtf.png](regla_fvg_mtf.png).
- «Toca» significa que el extremo del sweep entra en la zona del FVG. No hace falta que la cruce entera.
- Sin FVG tocado: no hay trade.

### Regla 3 · iFVG en LTF
- En M5 o M3, el tramo que lleva al extremo del sweep deja un FVG. Una vela que **cierra al otro lado de ese FVG** lo invierte (iFVG).
- Sin iFVG: no hay setup.
- El TF donde aparece el iFVG (M5 o M3) es el **TF de entrada** para el resto de reglas.

### Regla 4 · CISD (Change in State of Delivery)
- Se toma la secuencia de velas del mismo color que hizo el sweep (en cortos, las alcistas consecutivas que llegaron al extremo).
- El CISD es un **cierre más allá de la apertura de esa secuencia** (en cortos, un cierre por debajo de ella; en largos, por encima).
- Se mide en el TF del iFVG.

### Regla 5 · Entrada
Tres variantes, cada una con su propio backtest:

1. **Vela siguiente al CISD:** entrada a mercado a la apertura de la vela posterior a la que cierra el CISD.
2. **Retesteo del iFVG:** tras el CISD el precio continúa y vuelve a la zona del iFVG. Entrada al tocarla. Si no vuelve, no hay entrada.
3. **Primera vela sin mecha:** la primera vela a favor, sin mecha, en el TF de entrada tras el CISD. Se entra a la apertura de la vela siguiente.

## 4. Gestión

- **Stop:** en el extremo de la mecha que hizo el sweep (en cortos, su máximo; en largos, su mínimo). En el backtest no lleva colchón: el spread se descuenta como coste.
- **Objetivo:** 1:2 (2R).
- **Break even:** al llegar a 1R el stop pasa a la entrada.
- **Sesión:** a las 18:00 NY no se abren entradas y lo que siga abierto se cierra.
- Stop y objetivo en la misma vela: cuenta el stop.
- Una operación por sweep de HTF, sin reentradas tras el stop.
- **Más adelante:** estudiar si se puede llegar al extremo opuesto de la vela que marcó el rango (C1) como objetivo.

## 5. Definiciones operativas que hay que fijar al programar

Estas son las lecturas para el código. Se congelan antes de ver resultados.

| Concepto | Definición propuesta |
|---|---|
| FVG | Tres velas consecutivas en las que el máximo de la 1.ª es menor que el mínimo de la 3.ª (alcista), o el mínimo de la 1.ª es mayor que el máximo de la 3.ª (bajista). La zona es el hueco entre esos dos niveles |
| FVG ya formado | La 3.ª vela está cerrada antes de que empiece el sweep |
| iFVG | Cierre de una vela al otro lado de un FVG del tramo del sweep. Se toma el cierre, no la mecha |
| Secuencia del sweep | Velas consecutivas del mismo color que terminan en la vela que marca el extremo del sweep |
| Alineación de H3 | Velas H3 agregadas de M5 y alineadas a las 18:00 NY (18, 21, 0 ... 15), no a la hora del servidor |
| Sin mitigar | Desde que se forma el FVG de MTF hasta el inicio del sweep, ningún precio ha entrado en su zona |
| Más allá de C1 | La base de la zona está estrictamente por encima del máximo de C1 (cortos) / el techo por debajo del mínimo (largos): `Rule.fvg_above` |
| Antigüedad del FVG | Máximo 10 días (sensibilidad: 3 y 30) |
| Toca | El extremo del sweep cae dentro de la zona del FVG (sensibilidad: con tolerancia del 0,05 %) |
| Cierre dentro del rango | En vivo no se conoce hasta el final de C2. El CISD **no** lo exige: es solo el cierre más allá de la apertura de la secuencia (corrección del 03/11/2026: antes se exigía además un cierre dentro del rango de C1 y retrasaba la entrada; sigue como sensibilidad `inside_c1`). Para exigirlo de verdad: variante `--esperar-c2` |
| Ventana del CISD | Dentro de C2 |
| Entrada 2 (retesteo) | Orden límite en la base del iFVG tras una continuación (nuevo mínimo bajo el de la vela del CISD). Se cancela si toca el stop o el objetivo antes |
| Entrada 3 (sin mecha) | Vela bajista con máximo = apertura (cortos); entrada en la apertura de la siguiente |
| Costes | Spread real de MT5 en la vela de entrada |

## 6. Mercados y muestra

| Parámetro | Propuesta |
|---|---|
| Mercado | NAS100 de PUPrime; USTEC de MetaQuotes como control |
| Selección | 2018-2022 |
| Validación | 2023 en adelante |
| Limitación | La profundidad del histórico en M3/M5 manda: hay que comprobar cuántos años hay disponibles |

## 7. Criterios de aceptación (propuesta, siguiendo el estilo del TBR)

Se evalúa cada variante de entrada. Se da por buena si:
1. NAS100 de PUPrime, todo el histórico disponible: ≥ 100 operaciones y R neto > +0.05 con t > 2.0.
2. R neto positivo en el periodo de selección y en el de validación.
3. R neto > 0 en el control (USTEC de MetaQuotes).

Los criterios se congelan antes de ejecutar. Si no pasa, se documenta igual en `docs/estrategia_crt/RESULTADOS.md`, como se hizo con el TBR. Se compararán las tres entradas contando que probar tres variantes aumenta la probabilidad de un falso positivo.

## 8. Riesgos conocidos

- **Pocas operaciones:** cuatro condiciones encadenadas pueden dejar muy pocos casos. Hay que ver el embudo (cuántos días pasan cada paso) antes de sacar conclusiones.
- **Subjetividad:** FVG, iFVG y CISD se definen distinto según quién los enseñe. En el bot son reglas numéricas, y los resultados dependen de esas lecturas.
- **Stop largo:** el stop va tras la mecha del sweep y la entrada llega después del giro, así que el riesgo puede ser grande. Conviene medir la distribución del riesgo en puntos.
- **Solapamiento con otros skills:** el TBR entra con la rotura de un rango; CRT entra cuando la rotura falla. Hay que comprobar que no duplican señales.

## 9. Siguientes pasos

1. ~~Escribir `scripts/backtest_crt.py`~~ hecho.
2. ~~Ejecutar las tres variantes de entrada sobre NAS100~~ hecho: no pasa (ver `RESULTADOS.md`).
3. Decidir qué hacer con el resultado (ver el resumen en `RESULTADOS.md` y la conversación).
4. Solo si alguna variante pasa: crear el skill `crt` en `tradingbot/skills/crt` (a partir de `_plantilla`) y añadirlo como perfil aparte en `config.toml`.
