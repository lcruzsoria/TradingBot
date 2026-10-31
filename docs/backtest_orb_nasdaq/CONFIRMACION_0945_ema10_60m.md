# Confirmación del ORB que termina a las 09:45 (fuera de muestra), con filtro EMA 10 en velas de 60 min

Script: `scripts/confirmar_orb_0945.py`. Solo lee velas de MT5.

## Hipótesis y criterios (fijados antes de ver estos datos)

- **Principal:** ORB de 45 min de 09:00 a 09:45 NY; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después; stop en el extremo opuesto + 20 % del ancho; objetivo 1:1; cierre a las 6 h. Con el spread real de MT5.
- **Datos nuevos** (no se miraron al elegir la hipótesis): SP500 y DJ30 de PUPrime, NAS100 de MetaQuotes.
- **Se confirma si** (1) R neto medio positivo con t > 1.65 en al menos 2 de los 3 conjuntos y (2) los 3 juntos dan R neto medio positivo con t > 2.0.

- **Filtro EMA 10 (60 min):** largos solo con el cierre de la rotura por encima de la EMA y cortos solo por debajo; si la primera rotura del día va contra la EMA, ese día no se opera.

## Datos

- SP500.s (puprime): 572.760 velas M5 del 10/09/2018 al 30/10/2026; velas a las 17 h NY (pausa diaria): 0. Descartadas por la EMA: 266 de 2077 roturas.
- DJ30.s (puprime): 572.854 velas M5 del 07/09/2018 al 30/10/2026; velas a las 17 h NY (pausa diaria): 0. Descartadas por la EMA: 237 de 2057 roturas.
- USTEC (metaquotes): 292.855 velas M5 del 06/07/2022 al 30/10/2026; velas a las 17 h NY (pausa diaria): 1351. Descartadas por la EMA: 120 de 1030 roturas.

## Veredicto

| Criterio | Valor | Cumple |
|---|---:|---:|
| R neto > 0 y t > 1.65 en al menos 2 de 3 | 1 de 3 | **no** |
| Los 3 juntos: R neto > 0 y t > 2.0 | +0.010 R, t +0.83 | **no** |

**No se confirma.**

## ORB principal (45 min, 09:00–09:45)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| SP500.s (puprime) | 1811 | 51.4 % | -0.004 | -8.1 | 0.99 | -29.0 | -0.22 |
| DJ30.s (puprime) | 1820 | 50.1 % | +0.004 | +6.5 | 1.01 | -40.3 | +0.19 |
| USTEC (metaquotes) | 910 | 53.7 % | +0.053 | +48.0 | 1.16 | -14.5 | +1.96 |
| Los 3 juntos | 4541 | 51.3 % | +0.010 | +46.4 | 1.03 | -49.0 | +0.83 |

Sin costes (R bruto):

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| SP500.s (puprime) | 1811 | 51.8 % | +0.024 | +42.9 | 1.06 | -21.5 | +1.15 |
| DJ30.s (puprime) | 1820 | 50.7 % | +0.020 | +36.9 | 1.06 | -34.7 | +1.08 |
| USTEC (metaquotes) | 910 | 54.3 % | +0.061 | +55.3 | 1.18 | -14.1 | +2.26 |
| Los 3 juntos | 4541 | 51.8 % | +0.030 | +135.1 | 1.08 | -44.1 | +2.41 |

Por lado:

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| SP500.s (puprime), long | 944 | 55.1 % | +0.037 | +35.2 | 1.10 | -15.2 | +1.33 |
| SP500.s (puprime), short | 867 | 47.3 % | -0.050 | -43.3 | 0.89 | -52.8 | -1.67 |
| DJ30.s (puprime), long | 923 | 53.3 % | +0.024 | +22.3 | 1.07 | -16.6 | +0.92 |
| DJ30.s (puprime), short | 897 | 46.8 % | -0.018 | -15.8 | 0.95 | -36.0 | -0.65 |
| USTEC (metaquotes), long | 486 | 59.5 % | +0.106 | +51.4 | 1.34 | -10.4 | +2.93 |
| USTEC (metaquotes), short | 424 | 47.2 % | -0.008 | -3.4 | 0.98 | -13.3 | -0.20 |

Por mitades del histórico:

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| SP500.s (puprime), 1.ª mitad | 906 | 50.6 % | -0.022 | -20.0 | 0.95 | -27.7 | -0.78 |
| SP500.s (puprime), 2.ª mitad | 905 | 52.2 % | +0.013 | +11.9 | 1.03 | -26.0 | +0.45 |
| DJ30.s (puprime), 1.ª mitad | 910 | 52.1 % | +0.004 | +3.7 | 1.01 | -28.9 | +0.15 |
| DJ30.s (puprime), 2.ª mitad | 910 | 48.1 % | +0.003 | +2.9 | 1.01 | -18.8 | +0.12 |
| USTEC (metaquotes), 1.ª mitad | 455 | 53.8 % | +0.078 | +35.3 | 1.23 | -10.3 | +2.00 |
| USTEC (metaquotes), 2.ª mitad | 455 | 53.6 % | +0.028 | +12.7 | 1.08 | -14.5 | +0.75 |

## Referencia: NAS100 de PUPrime (dentro de muestra, no cuenta para el veredicto)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| NAS100.s (puprime), sin EMA | 2074 | 53.1 % | +0.039 | +81.0 | 1.11 | -13.7 | +2.16 |
| NAS100.s (puprime), con EMA | 1852 | 53.5 % | +0.041 | +75.3 | 1.12 | -13.0 | +2.14 |

## Contexto: las otras duraciones que acaban a las 09:45 (no cuentan para el veredicto)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| SP500.s, 15 min (09:30–09:45) | 1750 | 51.3 % | -0.009 | -15.1 | 0.98 | -41.9 | -0.40 |
| SP500.s, 30 min (09:15–09:45) | 1784 | 51.3 % | -0.003 | -4.6 | 0.99 | -28.9 | -0.12 |
| SP500.s, 60 min (08:45–09:45) | 1843 | 51.8 % | +0.006 | +11.9 | 1.02 | -21.9 | +0.32 |
| DJ30.s, 15 min (09:30–09:45) | 1750 | 49.9 % | -0.006 | -10.9 | 0.98 | -42.4 | -0.31 |
| DJ30.s, 30 min (09:15–09:45) | 1792 | 50.3 % | +0.008 | +14.4 | 1.02 | -32.2 | +0.42 |
| DJ30.s, 60 min (08:45–09:45) | 1845 | 50.2 % | +0.010 | +18.9 | 1.03 | -37.3 | +0.56 |
| USTEC, 15 min (09:30–09:45) | 876 | 52.3 % | +0.035 | +30.8 | 1.09 | -14.8 | +1.22 |
| USTEC, 30 min (09:15–09:45) | 900 | 52.9 % | +0.044 | +39.6 | 1.12 | -14.1 | +1.58 |
| USTEC, 60 min (08:45–09:45) | 913 | 53.9 % | +0.058 | +53.2 | 1.18 | -13.4 | +2.21 |
