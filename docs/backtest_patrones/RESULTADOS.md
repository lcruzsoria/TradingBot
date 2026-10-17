# Backtest de los patrones Continuación y Reversión (M15, índices americanos)

Script: `scripts/backtest_patrones.py` → `analisis/backtest_patrones.xlsx` (no se sube a git). Solo lee velas de MT5.

## Cómo se hizo

- **Datos:** NAS100.r, SP500.r, DJ30.r y US2000.r, velas M15 (bid) del 22/07/2022 al 16/10/2026: ~100.000 velas por mercado, que es el
  máximo que da el terminal («Máx. barras en el gráfico» = 100.000; si se sube en MT5, se puede repetir con más historia).
- **Patrones:** los del bot (`tradingbot.skills.pattern`), con las mismas reglas que en vivo, en cada TBR (Asia, London, NY Open) de cada
  día, con su plazo hasta la TBR siguiente: 3.280 TBR por mercado.
- **Operación:** entrada límite en el 0,5 del fibonacci, stop en el nivel 1 (swing o mecha pivote) y objetivo en el -0,5 (2R). Si caben
  stop y objetivo en una misma vela, cuenta el stop. Si en 24 h no pasa nada, se cierra al cierre de esa vela.
- **Costes:** spread real de MT5 en la vela de la entrada, una vez por operación (no incluye comisiones ni deslizamiento).
- **Sesgo:** el del bot (ruptura x2, TDO x2, Midnight x1, continuación x2, umbral 3, filtro de lateralidad), calculado con las velas M15 y
  congelado al abrirse cada bloque de 3 h, sin mirar al futuro. «A favor del sesgo» es lo que dejaría pasar Cortex.

## Resultado

**Ninguno de los dos patrones tiene ventaja: con un objetivo de 2R ganan el 33 % de las veces, que es justo el punto de equilibrio, y el
spread los deja en pérdida.**

| Patrón / filtro | Operaciones | Win rate | R medio (neto) | R total | Profit factor | Máx. drawdown | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| Continuación, sin filtro | 4.595 | 32,9 % | -0,125 | -575 | 0,83 | -577 R | -6,0 |
| Continuación, a favor del sesgo | 2.275 | 33,1 % | -0,114 | -260 | 0,84 | -260 R | -3,9 |
| Reversión, sin filtro | 1.468 | 33,0 % | -0,174 | -256 | 0,78 | -276 R | -4,7 |
| Reversión, a favor del sesgo | 131 | 34,4 % | -0,094 | -12 | 0,87 | -36 R | -0,7 |
| Ambos, sin filtro | 6.063 | 32,9 % | -0,137 | -831 | 0,82 | -836 R | -7,6 |

- **Sin costes** el R medio es -0,023 (Continuación, t = -1,1) y -0,011 (Reversión, t = -0,3): ventaja nula. Los costes son 0,117 R por
  operación de media (el spread frente a un stop corto), y es lo que los hace perder.
- **El sesgo no lo arregla:** a favor del sesgo sale algo menos mal (-0,11 R), pero sigue siendo negativo; en contra, -0,17 R.
- **Objetivo:** ninguna variante gana (1R: -0,12; 1,5R: -0,14; 2R: -0,14; 2,5R: -0,11; 3R: -0,10 R). El tiempo máximo (12, 24 o 48 h) no
  cambia nada.
- **Por mercado** (R medio neto): NAS100.r -0,035, DJ30.r -0,075, SP500.r -0,194, US2000.r -0,246. El NAS100 es el menos malo (t = -1,0).
- **Dirección:** los largos pierden menos (-0,07 Continuación) que los cortos (-0,18): los índices han subido en el periodo.
- **Zona:** Continuación en NY Open es la peor (win rate 28 %); Reversión en NY Open la menos mala (-0,11).
- **Robustez:** pierde en las dos mitades del histórico (-0,17 la 1ª, -0,10 la 2ª).
- **Embudo:** Continuación da entrada en el 35 % de las TBR (53 % de las que se activan); Reversión, en el 11 % (27-31 % de las activadas).

## Qué significa

El win rate es el de un precio sin memoria: con un objetivo de 2R, ganar el 33 % da ganancia bruta cero. Los patrones definen con precisión
dónde entrar, pero no aportan una probabilidad mayor que el azar de llegar al -0,5 antes que al swing, y el spread de los índices hace
que cada operación cueste 0,12 R. Lo que se haga a partir de aquí tendría que ganar más de ~0,12 R por operación solo para empatar.

## Límites

Un solo broker, ~4 años y entradas simuladas con velas M15 (sin ver el recorrido interno de la vela). Cada operación vale 1R y se cuenta por
separado: sin límite de operaciones simultáneas ni gestión de riesgo.
