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
| iFVG, CISD y entrada | M15 o M5 (TF del iFVG ≤ TF del FVG) | M15 o M5 |

- Mercados (`CRT_SYMBOLS`): NAS100.s, SP500.s, DJ30.s, EURUSD y GBPUSD de PUPrime.
- Sesión: a las **18:00 NY** (índices) o **17:00 NY** (forex) no se abren entradas y lo abierto se cierra.
- Perfil aparte en el bot (`crt`), con su propia skill y sin Pattern, TBR ni Calendario. No usa el sesgo.

## 3. Reglas

Se evalúan en este orden y todas son obligatorias. **Todo ocurre dentro de C2.**

1. **Sweep.** C2 supera con una mecha el mínimo de C1 (largo) o su máximo (corto). El primer extremo que toma C2 manda: si ya había tomado el otro, el sweep es el del otro lado. Si el precio llega al extremo opuesto de C1 sin que el setup se complete, queda **invalidado**.
1b. **Qué barre C2.** No hace falta que sea el extremo de C1: vale cualquier nivel anterior que siga intacto (ninguna vela HTF lo ha superado desde que se formó): el **PDH/PDL** (máximo/mínimo del día anterior), un **swing de H4** (pivote clásico de 3 velas, hasta 10 días atrás) o el máximo/mínimo de una **vela de H12** de los últimos 10 días. El patrón arranca con el primer nivel que supera el precio y la etiqueta (ficha del gráfico, línea «Sweep», y motivo de la señal) dice el más profundo que barre C2: «vela C1», «PDH día dd/mm», «PDL día dd/mm», «swing H4 dd/mm hh:mm» o «máx/mín H12 dd/mm hh:mm». Un nivel intacto está siempre más allá del extremo de C1, así que apenas añade setups nuevos (en el histórico, unos 3 sobre 2 200): cambia sobre todo cuál se nombra.
2. **Doble FVG y zona común.** Dentro de C2 hay un FVG «normal» (M15 o M5) y un iFVG de 15 o 5 min que **se solapan**; el hueco que comparten es la **zona común**. **El primer hueco en nacer es siempre el iFVG** (el que se invierte y da el CISD): tiene que seguir activo, sin cerrarse del todo con mecha o cuerpo ni invertirse, hasta que se forma el FVG normal, que nace después. Con los dos formados, el pullback puede rellenar el FVG para rebotar; lo que invalida la pareja es el cierre con cuerpo al otro lado de la zona (punto 5).
   - **FVG e iFVG pueden ser de 15 o 5 min**, con **TF del FVG ≥ TF del iFVG**: FVG M15 con iFVG de M15 o M5; FVG M5 con iFVG de M5. No pueden ser el mismo hueco. Las combinaciones con 3 min se probaron y se quitaron: dan muchos setups y salen peor (`RESULTADOS_zona.md`).
   - **El CISD y la entrada son del TF del iFVG:** si el FVG y el iFVG se detectan en 15 min, el cierre sobre el CISD se mira en velas de 15 min y la entrada es a la apertura de la siguiente vela de 15 min; con un iFVG de 5 min, en velas de 5 min. Cada combinación se evalúa con las velas de su TF.
   - Se busca siempre la combinación del **TF mayor posible**, marcado por el FVG: si hay varias, manda la del FVG de mayor TF (M15 antes que M5). Si dos combinaciones dan entrada en la misma C2 y lado, vale la primera que cierra sobre su CISD.
   - Ambos nacen dentro de C2 (su primera vela empieza en C2 o después).
3. **CISD.** Es el extremo de la **secuencia de velas del mismo color que genera el iFVG** (3 velas, pero pueden ser 4, 5 o más): en un largo, el **máximo** de las velas bajistas seguidas; en un corto, el mínimo. Se mide en el **TF donde se crea el BPR** (el del FVG): con un FVG M15, la secuencia y el cierre sobre el CISD son de velas de 15 min. El CISD queda siempre más allá del BPR (largo: un máximo por encima de él).
4. **Inversión.** El iFVG se invierte cuando una vela cierra al otro lado de su base (largo: por encima de su techo).
5. **Pullback al BPR.** La zona común de los dos huecos se llama **BPR** (balanced price range) y es la **única zona de retest válida** tras crearse el FVG: tocar el FVG sin tocar el BPR no vale. Ambos huecos pueden ser más grandes que el BPR. Con el iFVG ya invertido y los dos FVG formados, el precio vuelve a la zona común (largo: **de arriba abajo**): una vela posterior a la inversión la toca con la mecha sin cerrar al otro lado de ella.
   - **Un retest que cierra con cuerpo al otro lado de la zona invalida esa pareja:** si tras el retest (o en él) una vela cierra con el cuerpo por debajo de la zona común (en un largo), esa pareja iFVG + FVG muere. Tiene que haber un **rebote** y a continuación el cierre sobre el CISD; si no, se busca otra pareja, normalmente un doble FVG más abajo. Cada pareja iFVG + FVG lleva su propio estado (inversión, retest e invalidación).
6. **Entrada.** Tras el pullback, la primera vela **del TF del BPR** que **cierra con el cuerpo más allá del CISD** (largo: por encima; una mecha que lo supera no cuenta) da la señal. **Sin cierre sobre el CISD no hay entrada**: ese es el filtro que evita muchos stops. Se entra a la **apertura de la vela siguiente** (`CRT_ENTRY=1`; con `4`, al cierre de esa vela). Antes de que cierre C2.
7. **«Setup OK sin Entrada».** Si la zona común existe y el iFVG se invierte pero el precio **sigue sin volver a ella** (llega al extremo opuesto de C1 o acaba C2), no hay entrada: el gráfico marca el CRT como «Setup OK sin Entrada», con el FVG, el iFVG, la zona común y el CISD. Es solo una anotación.

### Ejemplo real: la pareja invalidada y la de más abajo (NAS100)
NAS100.s, 03/11/2026, C2 de las 00:00 (H3), largo: **no es setup**. El FVG de M5 27966.4-27969.9 (01:10-01:20 NY) lo mitiga la mecha de las 01:25 NY, mucho antes de que nazca el iFVG de 27951.7-27981.9 (02:00-02:10 NY), así que esa pareja no vale (antes se operaba entrando a las 02:50 en 28024.9). Las velas están en `tests/crt_nas100_20261103.py`.

### Ejemplo real
EURUSD, 02/11/2026, C2 de las 21:00 NY (H4), largo: sweep del mínimo de C1 (1.11808) y mínimo de C2 en 1.1177; FVG M15 1.11814-1.11833 e iFVG M5 1.11815-1.11834 (BPR 1.11815-1.11833); inversión a las 21:55; pullback al BPR a las 22:10 (mínimo 1.11825); el CISD (1.11891, el máximo de la secuencia bajista que genera el iFVG) se supera con cuerpo en la vela M15 de 22:45, que cierra a las 23:00. **Entrada a las 23:00 en 1.11902**, stop 1.1177 (13,2 pips, dentro del límite de 25), objetivo 2R en 1.12166.

`tests/crt_eurusd_20261102.py` trae las velas y los tests comprueban cada paso.

## 4. Gestión

- **Stop máximo:** si la distancia de la entrada al stop supera **25 pips en forex o 125 puntos en índices** la entrada se cancela (`CRT_MAX_SL_FOREX_PIPS`, `CRT_MAX_SL_INDICES_POINTS`; 0 = sin límite).

- **Stop:** en el extremo del sweep hasta ese momento (largo: el mínimo de C2; corto: el máximo). Sin colchón.
- **Objetivo:** `CRT_RR` veces el riesgo (2R).
- **Breakeven:** en cuanto el precio toca +1 R el stop pasa a la entrada (lo lleva Setup).
- **Sesión:** a la hora de cierre no se abren entradas y lo abierto se cierra.
- Stop y objetivo en la misma vela: cuenta el stop. Una operación a la vez por mercado; el bot no abre otra mientras haya una abierta.

## 5. En el bot

- **Skill `crt`** (`tradingbot/skills/crt/skill.py`): con cada `candles.loaded` de M5 busca el setup con `engine.find_zone_setups` y `engine.entry_point`, y publica `crt.signal`; Cortex la convierte en orden para Setup (simulada) sin consultar el sesgo.
- **Gráfico (botón CRT):** dibuja, además de los CRT del backtest antiguo, **la operación activa de Cortex con todos sus niveles** (`crt/chart.py: live_marks`): el FVG, el iFVG (con el TF), la zona común (recuadro), el CISD, el punto del pullback y la posición (entrada, stop y objetivo); los **setups válidos que el bot no operó** (`signal_marks`), con el resultado que habrían dado sobre las velas cargadas (TP, SL, BE o abierta), y los **«Setup OK sin Entrada»** (`no_entry_marks`). Los setups se calculan una vez con las velas de la skill (M5 o M3) y se dibujan igual en cualquier timeframe del gráfico (en 15m o 1h tienen el mismo estado que en 5m). La etiqueta discreta solo lleva el resultado; los TF del FVG y del iFVG, sus zonas, la zona común, el retest y el CISD salen al desplegarla (ficha). El setup no se guarda con la orden: se vuelve a buscar con el motor sobre las velas cargadas (solo si el gráfico está en el TF de la orden).
- **Backtest:** `scripts/backtest_crt_zona.py` (velas M5 de `analisis/m5`), con el mismo motor.

## 5 bis. Sesgo del perfil CRT (activo en modo informativo)

Sesgo propio del perfil, independiente del de los demás (el perfil CRT no lleva la skill Bias): puntúa cada setup con las **zonas de reversión en HTF** (1h, 4h o 1d) que lo respaldan. Va en el bloque `CRT_BIAS_*` de `tradingbot.env` y la tarjeta de sesgo enseña el del último setup.

- **Dirección:** soporte para los largos y resistencia para los cortos.
- **Cada regla da un punto** (FVG, rejection block y order block: de 0 a 3). Con **puntos ≥ `CRT_BIAS_MIN_SCORE` (1)** el setup es GO; si no, NO GO.
- **Validación por regla y de mayor a menor TF** (1d, 4h, 1h): en cuanto una regla se cumple en un TF, ese TF le da el punto y no se sigue con los menores (p. ej. si el setup se forma dentro de un FVG de 1d, no hace falta mirar el FVG de 4h ni de 1h).
- **`CRT_BIAS_ENFORCE=false` (por defecto):** el sesgo se calcula y se enseña (tarjeta, orden y señal) pero **no anula ningún trade**: el setup es GO aunque no llegue a los puntos. Con `true`, un setup por debajo de `CRT_BIAS_MIN_SCORE` es NO GO.
- **Apagado (`CRT_BIAS_ENABLED=false`):** el sesgo es 0 y el setup es siempre GO.
- **Vigencia:** la zona tiene que haberse creado **antes de la C2** del setup (la vela del patrón doble FVG + CISD) y como mucho `CRT_BIAS_LOOKBACK_DAYS` (10) días antes de su hora de creación.
- **«Dentro de la zona»:** la zona común del CRT (FVG ∩ iFVG) se solapa con la zona HTF.

| Zona | Definición (largo; el corto es el espejo) |
|---|---|
| **FVG en HTF** | Hueco entre el máximo de la vela 1 y el mínimo de la vela 3, a la izquierda del precio |
| **Rejection block** | La mecha de un swing low (su mínimo es el más bajo de `CRT_BIAS_SWING_WIDTH`=1 vela a cada lado) que ocupa más del `CRT_BIAS_RB_MIN_WICK_PCT`=50 % de su vela: del mínimo al borde inferior del cuerpo |
| **Order block** | El rango completo de la última vela bajista antes de una vela alcista de impulso que deja un FVG (el máximo de la bajista queda bajo el mínimo de la vela posterior). **Sin FVG no hay OB** |

Parámetros: `CRT_BIAS_ENABLED`, `CRT_BIAS_ENFORCE`, `CRT_BIAS_LOOKBACK_DAYS`, `CRT_BIAS_MIN_SCORE`, `CRT_BIAS_TFS`, `CRT_BIAS_SWING_WIDTH`, `CRT_BIAS_RB_MIN_WICK_PCT`. Código: `tradingbot/skills/crt/bias.py`; la señal `crt.signal` lleva `bias_points` y Cortex decide con ellos.

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
