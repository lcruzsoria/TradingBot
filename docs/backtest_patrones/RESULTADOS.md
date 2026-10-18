# Backtest de los patrones Continuación y Reversión (M15, índices americanos)

Script: `scripts/backtest_patrones.py` → `analisis/backtest_patrones.xlsx` (no se sube a git). Solo lee velas de MT5.

## Cómo se hizo

- **Datos:** NAS100.r, SP500.r y DJ30.r del 7-10/09/2018 al 16/10/2026 y US2000.r del 31/07/2020 al 16/10/2026: unas 190.000 velas M15
  por mercado (146.000 el US2000). **Antes de 2018 el broker solo tiene velas diarias** (aunque el terminal las muestre como M15), así que se
  descartan automáticamente: el histórico intradía real es de ~8 años. Para llegar aquí hubo que subir «Máx. barras en el gráfico» en MT5
  (antes, 100.000 velas por mercado: solo 4 años).
- **Patrones:** los del bot (`tradingbot.skills.pattern`), con las mismas reglas que en vivo, en cada TBR (Asia, London, NY Open) de cada
  día, con su plazo hasta la TBR siguiente: ~6.300 TBR por mercado.
- **Operación:** entrada límite en el 0,5 del fibonacci, stop en el nivel 1 (swing o mecha pivote) y objetivo en el -0,5 (2R). Si caben
  stop y objetivo en una misma vela, cuenta el stop. Si en 24 h no pasa nada, se cierra al cierre de esa vela.
- **Costes:** spread real de MT5 en la vela de la entrada, una vez por operación (no incluye comisiones ni deslizamiento).
- **Sesgo:** el del bot (ruptura x2, TDO x2, Midnight x1, continuación x2, umbral 3, filtro de lateralidad), calculado con las velas M15 y
  congelado al abrirse cada bloque de 3 h, sin mirar al futuro. «A favor del sesgo» es lo que dejaría pasar Cortex.

## Resultado

**Ninguno de los dos patrones tiene ventaja: con un objetivo de 2R ganan el 33,6 % de las veces, que es el punto de equilibrio, y el
spread los deja en pérdida.**

| Patrón / filtro | Operaciones | Win rate | R medio (neto) | R total | Profit factor | Máx. drawdown | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Continuación, sin filtro | 7.822 | 33,2 % | -0,096 | -754 | 0,87 | -791 R | -6,0 |
| Continuación, a favor del sesgo | 3.891 | 33,7 % | -0,077 | -300 | 0,89 | -319 R | -3,4 |
| Reversión, sin filtro | 2.562 | 34,7 % | -0,097 | -249 | 0,87 | -335 R | -3,4 |
| Reversión, a favor del sesgo | 226 | 35,4 % | -0,047 | -11 | 0,94 | -41 R | -0,5 |
| Ambos, sin filtro | 10.384 | 33,6 % | -0,097 | -1.003 | 0,87 | -1.043 R | -6,9 |

- **Sin costes** el R medio es -0,010 (Continuación), +0,039 (Reversión) y +0,002 en conjunto (t = 0,15): ventaja nula. Los costes son 0,099 R
  por operación de media (el spread frente a un stop corto), y es lo que los hace perder.
- **El sesgo no lo arregla:** a favor del sesgo sale algo menos mal (-0,075 R), pero sigue siendo negativo; en contra, -0,078 R.
- **Objetivo:** ninguna variante gana (1R: -0,098; 1,5R: -0,101; 2R: -0,097; 2,5R: -0,079; 3R: -0,077 R). El tiempo máximo (12, 24 o 48 h) no
  cambia nada.
- **Por mercado** (R medio neto): NAS100.r -0,012, DJ30.r -0,048, SP500.r -0,141, US2000.r -0,215. El NAS100 es el menos malo (t = -0,4).
- **Zona:** Asia es la peor (-0,24 R), London la menos mala (-0,05 R).
- **Por año:** 2018 +0,08 R (304 operaciones), 2019-2022 entre -0,07 y -0,05, 2023 -0,19, 2024 -0,16, 2025 -0,09, 2026 -0,11.
- **Robustez:** pierde en las dos mitades del histórico (-0,050 la 1ª, -0,143 la 2ª).
- **Embudo:** Continuación da entrada en el 32-34 % de las TBR (49-54 % de las que se activan); Reversión, en el 10-12 % (28-32 % de las activadas).

## Qué significa

El win rate es el de un precio sin memoria: con un objetivo de 2R, ganar el 33 % da ganancia bruta cero. Los patrones definen con precisión
dónde entrar, pero no aportan una probabilidad mayor que el azar de llegar al -0,5 antes que al swing, y el spread de los índices hace
que cada operación cueste ~0,1 R. Lo que se haga a partir de aquí tendría que ganar más de ~0,1 R por operación solo para empatar. La
búsqueda de subconjuntos (`SUBCONJUNTOS.md`) encuentra una pista en los largos de lunes.

## Cambio del 18/10/2026: la Reversión se anula con una rotura con cuerpo antes de la entrada

Desde ahora, si ya confirmada la mecha pivote una vela cierra fuera del lado tomado antes del retroceso al 0,5, la Reversión se anula (es
continuación). Backtest regenerado con los plazos y filtros actuales del bot (mismo histórico) y comparado con el anterior:

| Mercados | Reversiones antes → después | R medio Reversión (sin filtro) | Lo que opera el bot (R neto total) |
|---|---:|---:|---:|
| Índices americanos | 3.441 → 3.408 | -0,098 → -0,094 | -295,5 → -290,9 |
| Forex (EURUSD, GBPUSD) | 6.671 → 6.567 | -0,218 → -0,223 | -1.944,4 → -2.029,9 |
| Oro (XAUUSD) | 1.007 → 996 | -0,098 → -0,100 | -168,0 → -169,8 |
| Cripto (BTCUSD; ETH, con spread poco fiable, aparte) | 1.829 → 1.802 | -0,845 → -0,849 | -40,4 → -28,4 |

- Quita en torno al 1-1,5 % de las reversiones. En índices, las 33 que desaparecen ganaban el 21 % (-0,51 R de media).
- **No cambia la conclusión:** ningún grupo pasa a tener ventaja. En lo que opera el bot (GO de Cortex, una posición a la vez, una sesión
  un trade) la sesión que deja libre la reversión anulada la ocupa a veces otra entrada, y el total queda prácticamente igual (-2.448 →
  -2.519 R sin ETH; la diferencia es casi toda de forex). El motivo del cambio es de coherencia: no dar en la misma sesión un largo de
  Reversión y un corto de Continuación por la misma rotura.
- No evita todos los casos de entradas opuestas en una sesión: si la Reversión ya entró antes de la rotura (SP500, London del 16/10/2026),
  las dos siguen siendo válidas. Ahí Cortex solo opera la primera, y el gráfico marca la otra como NO GO.

## Límites

Un solo broker, ~8 años y entradas simuladas con velas M15 (sin ver el recorrido interno de la vela). Cada operación vale 1R y se cuenta por
separado: sin límite de operaciones simultáneas ni gestión de riesgo.
