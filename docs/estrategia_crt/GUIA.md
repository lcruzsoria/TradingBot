# CRT (Candle Range Theory): guía de la estrategia

Estado (02/11/2026): **el setup se define dentro de C2** (definición del usuario, ver sección 3). Con ella ninguna combinación pasa los criterios: lo mejor es NAS100 M3 con el retesteo del iFVG (+0.027 R, t +0.74); forex sigue negativo. Resultados en [RESULTADOS.md](RESULTADOS.md) y los RESULTADOS_*.md; script en `scripts/backtest_crt.py`. Ejemplo dibujado: [setup_c2_2026-10-28.png](setup_c2_2026-10-28.png) (EURUSD, largo). Los dibujos `reglas_crt`, `criterios_htf_mtf`, `regla_fvg_mtf`, `entradas_crt` y `operacion_*` son de la definición anterior (FVG que ya existía y que el extremo tocaba) y están desfasados.

## 1. Idea

Tres velas de un timeframe alto (HTF): **C1 = rango** (acumulación), **C2 = manipulación** y **C3 = expansión**. C2 barre con una mecha un extremo de C1; el desplazamiento posterior deja un desequilibrio (FVG) en un timeframe medio, el precio vuelve a él y en un timeframe bajo se busca la confirmación del giro y se entra, antes de que C2 cierre.

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

Todas son obligatorias y se evalúan en este orden. Si falta una, no hay trade. **Todo ocurre dentro de C2**: no se espera a saber si C2 cierra dentro del rango de C1 (eso se descartó como filtro porque solo se conoce al final de C2).

### Paso 1 · Sweep en HTF (liquidez externa)
- Una vela HTF (C2) supera con una mecha el máximo (o mínimo) de la vela anterior (C1). El extremo del sweep es el máximo de C2 hasta el momento; si C2 hace un máximo nuevo, el setup se reinicia con ese extremo.
- Si C2 supera también el otro extremo de C1 antes de la entrada, no hay sesgo y no se opera.
- Máximo barrido → **corto**. Mínimo barrido → **largo**.

### Paso 2 · FVG de MTF que nace del desplazamiento, y vuelta a él
- Tras el extremo del sweep, el desplazamiento deja un **FVG de M15, M30 o H1** en la dirección contraria al sweep (corto: FVG **bajista**; largo: FVG alcista). El FVG tiene que nacer **después** del extremo: su primera vela termina después de él. Vale cualquiera de los tres timeframes.
- El precio **vuelve** a ese FVG: basta con que lo toque una mecha (no hace falta cerrar dentro).
- Sin vuelta al FVG: no hay trade.

### Paso 3 · iFVG en LTF = CISD
- En M5, M3 o M1, tras el toque al FVG de MTF aparece un FVG de LTF en la dirección del sweep (corto: alcista). Una vela que **cierra al otro lado de su base** lo invierte (iFVG). **Esa inversión es el CISD.**
- El FVG de LTF se forma **después del toque** (su tercera vela cierra tras el toque), no está ya invertido y **no tiene plazo**: puede invertirse mucho después del toque.
- El TF donde aparece el iFVG (M5, M3 o M1) es el **TF de entrada**.

### Paso 4 · Entrada
Cuatro variantes, cada una con su propio backtest, siempre **antes de que cierre C2**:

1. **Vela siguiente al CISD:** entrada a mercado a la apertura de la vela posterior a la que cierra el CISD.
2. **Retesteo del iFVG:** tras el CISD el precio continúa y vuelve a la zona del iFVG. Entrada al tocarla. Si no vuelve, no hay entrada.
3. **Primera vela sin mecha:** la primera vela a favor, sin mecha, en el TF de entrada tras el CISD. Se entra a la apertura de la vela siguiente.
4. **Cierre del CISD:** entrada a mercado al cierre de la propia vela que cierra el CISD, sin esperar a la siguiente.

## 4. Gestión

- **Stop:** en el extremo de la mecha que hizo el sweep (en cortos, su máximo; en largos, su mínimo). En el backtest no lleva colchón: el spread se descuenta como coste.
- **Objetivo:** 1:2 (2R).
- **Break even:** al llegar a 1R el stop pasa a la entrada.
- **Sesión:** a las 18:00 NY no se abren entradas y lo que siga abierto se cierra.
- Stop y objetivo en la misma vela: cuenta el stop.
- Una operación por sweep de HTF, sin reentradas tras el stop.
- **Objetivo alternativo (`--objetivo-c1`):** el extremo opuesto de C1 (si se tomó el máximo, va a por el mínimo). Regla 1: si ese extremo da menos de 2 R, el setup se descarta y se anota el R máximo que habría dado.

## 5. Definiciones operativas que hay que fijar al programar

Estas son las lecturas para el código. Se congelan antes de ver resultados.

| Concepto | Definición propuesta |
|---|---|
| FVG | Tres velas consecutivas en las que el máximo de la 1.ª es menor que el mínimo de la 3.ª (alcista), o el mínimo de la 1.ª es mayor que el máximo de la 3.ª (bajista). La zona es el hueco entre esos dos niveles |
| FVG nacido tras el extremo | La primera vela del FVG de MTF termina después de la vela LTF del extremo del sweep, y su 3.ª vela cierra (se forma) antes de la vela LTF que se evalúa |
| iFVG | Cierre de una vela al otro lado de la base de un FVG de LTF posterior al extremo. Se toma el cierre, no la mecha |
| Alineación de H3 | Velas H3 agregadas de M5 y alineadas a las 18:00 NY (18, 21, 0 ... 15), no a la hora del servidor (forex: H4 alineadas a las 17:00) |
| Vuelta al FVG | Una vela LTF cuyo extremo (corto: máximo) entra en la zona del FVG de MTF, ya formado. Sin tolerancia |
| Ventana del setup | Dentro de C2: el CISD y la apertura de la entrada ocurren antes del cierre de C2 |
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

Los criterios se congelan antes de ejecutar. Si no pasa, se documenta igual en `docs/estrategia_crt/RESULTADOS.md`, como se hizo con el TBR. Se compararán las cuatro entradas contando que probar cuatro variantes aumenta la probabilidad de un falso positivo.

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
