# CRT (Candle Range Theory): guía de la estrategia

Estado (03/11/2026): **la skill opera la «zona común»** (definición del usuario, secciones 1 a 4). En el backtest no hay ventaja: bruto ≈ 0 R y neto negativo en todos los mercados y objetivos (ver [RESULTADOS_zona.md](RESULTADOS_zona.md)); el perfil CRT sirve para forwardtest en simulación. Los `RESULTADOS.md`, `RESULTADOS_forex.md` y los dibujos `reglas_crt`, `criterios_htf_mtf`, `regla_fvg_mtf`, `entradas_crt`, `operacion_*` y `setup_c2_*` son de definiciones anteriores (FVG que el extremo tocaba, iFVG tras el toque) y están desfasados.

## 1. Idea

Tres velas de un timeframe alto (HTF): **C1 = rango**, **C2 = manipulación** y **C3 = expansión**. C2 barre con una mecha un extremo de C1 y, dentro de C2, dos FVG de distinto timeframe se solapan. Cuando el precio invierte el de menor TF, vuelve a la zona que comparten y cierra más allá del CISD, se entra a favor del giro antes de que C2 cierre.

Se describe el largo (barrido de un mínimo); el corto es el espejo exacto. En el largo los dos FVG son **bajistas** (zonas de resistencia que el precio cruzó al caer).

## 2. Timeframes y mercado

| Papel | Índices | Forex |
|---|---|---|
| HTF (sweep) | H3 | H4 |
| FVG «normal» | M15 o M5 | M15 o M5 |
| iFVG, CISD y entrada | M5 o M3 (el timeframe del gráfico) | M5 o M3 |

- Mercados (`CRT_SYMBOLS`): NAS100.s, SP500.s, DJ30.s, EURUSD y GBPUSD de PUPrime.
- Sesión: a las **18:00 NY** (índices) o **17:00 NY** (forex) no se abren entradas y lo abierto se cierra.
- Perfil aparte en el bot (`crt`), con su propia skill y sin Pattern, TBR ni Calendario. No usa el sesgo.

## 3. Reglas

Se evalúan en este orden y todas son obligatorias. **Todo ocurre dentro de C2.**

1. **Sweep.** C2 supera con una mecha el mínimo de C1 (largo) o su máximo (corto). El primer extremo que toma C2 manda: si ya había tomado el otro, el sweep es el del otro lado. Si el precio llega al extremo opuesto de C1 sin que el setup se complete, queda **invalidado**.
2. **Doble FVG y zona común.** Dentro de C2 hay un FVG «normal» (M15 o M5) y un iFVG de las velas del gráfico (M5 o M3) que **se solapan**; el hueco que comparten es la **zona común**.
   - El iFVG es de un **TF igual o menor** que el del FVG: con un FVG de M15 vale un iFVG de M5 o M3; con un FVG de M5, M5 o M3, pero no M15. No pueden ser el mismo hueco.
   - Se busca siempre la combinación del **TF mayor posible**, marcado por el FVG: si hay varias, manda la del FVG de mayor TF (M15 antes que M5).
   - Ambos nacen dentro de C2 (su primera vela empieza en C2 o después).
3. **CISD.** Es el extremo de la vela que creó el iFVG: la vela central de sus tres velas (largo: su **máximo**; corto: su mínimo).
4. **Inversión.** El iFVG se invierte cuando una vela cierra al otro lado de su base (largo: por encima de su techo).
5. **Pullback a la zona común.** Con el iFVG ya invertido y los dos FVG formados, el precio vuelve a la zona común (largo: **de arriba abajo**): una vela posterior a la inversión la toca con la mecha sin cerrar al otro lado de ella.
6. **Entrada.** Tras el pullback, la primera vela que **cierra con el cuerpo más allá del CISD** (largo: por encima) da la señal. Se entra a la **apertura de la vela siguiente** (`CRT_ENTRY=1`; con `4`, al cierre de esa vela). Antes de que cierre C2.
7. **«Setup OK sin Entrada».** Si la zona común existe y el iFVG se invierte pero el precio **sigue sin volver a ella** (llega al extremo opuesto de C1 o acaba C2), no hay entrada: el gráfico marca el CRT como «Setup OK sin Entrada», con el FVG, el iFVG, la zona común y el CISD. Es solo una anotación.

### Ejemplo real
EURUSD, 02/11/2026, C2 de las 21:00 NY (H4), largo:
- Sweep: el mínimo de C1 (1.11808) cae a las 21:15 y el low de C2 llega a 1.1177.
- FVG M15 bajista de las velas 21:00-21:30: 1.11814-1.11833. iFVG M5 de las velas 21:10-21:20: 1.11815-1.11834. Zona común: **1.11815-1.11833**.
- CISD: 1.11841 (máximo de la vela de las 21:15).
- Inversión: a las 21:55 una vela cierra en 1.1185, sobre 1.11834.
- Pullback: a las 22:10 el mínimo (1.11825) entra en la zona por arriba.
- Cierre sobre el CISD: la vela de las 22:25 cierra en 1.11843.
- **Entrada a las 22:30 en 1.11843**, stop 1.1177 (7,3 pips), objetivo 2R en 1.11989.

`tests/crt_eurusd_20261102.py` trae las velas y los tests comprueban cada paso.

## 4. Gestión

- **Stop:** en el extremo del sweep hasta ese momento (largo: el mínimo de C2; corto: el máximo). Sin colchón.
- **Objetivo:** `CRT_RR` veces el riesgo (2R).
- **Breakeven:** en cuanto el precio toca +1 R el stop pasa a la entrada (lo lleva Setup).
- **Sesión:** a la hora de cierre no se abren entradas y lo abierto se cierra.
- Stop y objetivo en la misma vela: cuenta el stop. Una operación a la vez por mercado; el bot no abre otra mientras haya una abierta.

## 5. En el bot

- **Skill `crt`** (`tradingbot/skills/crt/skill.py`): con cada `candles.loaded` de M3 o M5 busca el setup con `engine.find_zone_setups` y `engine.entry_point`, y publica `crt.signal`; Cortex la convierte en orden para Setup (simulada) sin consultar el sesgo.
- **Gráfico (botón CRT):** dibuja, además de los CRT del backtest antiguo, **la operación activa de Cortex con todos sus niveles** (`crt/chart.py: live_marks`): el FVG, el iFVG (con el TF), la zona común (recuadro), el CISD, el punto del pullback y la posición (entrada, stop y objetivo); los **setups válidos que el bot no operó** (`signal_marks`), con el resultado que habrían dado sobre las velas cargadas (TP, SL, BE o abierta), y los **«Setup OK sin Entrada»** (`no_entry_marks`). Los setups se calculan una vez con las velas de la skill (M5 o M3) y se dibujan igual en cualquier timeframe del gráfico (en 15m o 1h tienen el mismo estado que en 5m). La etiqueta discreta solo lleva el resultado; los TF del FVG y del iFVG, sus zonas, la zona común, el retest y el CISD salen al desplegarla (ficha). El setup no se guarda con la orden: se vuelve a buscar con el motor sobre las velas cargadas (solo si el gráfico está en el TF de la orden).
- **Backtest:** `scripts/backtest_crt_zona.py` (velas M5 de `analisis/m5`), con el mismo motor.

## 6. Definiciones operativas

| Concepto | Definición |
|---|---|
| FVG | Tres velas seguidas en las que el máximo de la 1.ª es menor que el mínimo de la 3.ª (alcista) o el mínimo de la 1.ª es mayor que el máximo de la 3.ª (bajista); la zona es el hueco entre esos niveles |
| FVG nacido en C2 | Su primera vela empieza en C2 o después; el FVG se considera formado al cierre de su 3.ª vela |
| iFVG invertido | Una vela del gráfico cierra al otro lado de la base del FVG de LTF (el cierre, no la mecha) |
| Toque | Una vela posterior a la inversión y a la formación de los dos FVG cuya mecha entra en la zona común sin cerrar al otro lado de ella |
| Alineación de HTF | Velas H3 alineadas a las 18:00 NY (índices) o H4 a las 17:00 NY (forex), no a la hora del servidor |
| Hora del servidor | NY + 7 h (se estima si el feed no la da) |

## 7. Riesgos conocidos

- **Sin ventaja demostrada:** el backtest da R bruto ≈ 0 en todas las variantes (ver `RESULTADOS_zona.md`).
- **Subjetividad:** FVG, iFVG y CISD se definen distinto según quién los enseñe; en el bot son reglas numéricas.
- **Zonas finas:** a veces la zona común mide pocos puntos; no hay un tamaño mínimo.
- **Operaciones antiguas:** las abiertas con la secuencia anterior no se dibujan con niveles (el motor no las encuentra con la regla nueva).
