# Confirmación del ORB que termina a las 09:45 (fuera de muestra)

Script: `scripts/confirmar_orb_0945.py`. Solo lee velas de MT5.

## Hipótesis y criterios (fijados antes de ver estos datos)

- **Principal:** ORB de 45 min de 09:00 a 09:45 NY; entrada al cierre de la primera vela M5 que cierra fuera del ORB, como tarde 6 h después; stop en el extremo opuesto + 20 % del ancho; objetivo 1:1; cierre a las 6 h. Con el spread real de MT5.
- **Datos nuevos** (no se miraron al elegir la hipótesis): SP500 y DJ30 de PUPrime, NAS100 de MetaQuotes.
- **Se confirma si** (1) R neto medio positivo con t > 1.65 en al menos 2 de los 3 conjuntos y (2) los 3 juntos dan R neto medio positivo con t > 2.0.

## Datos

- SP500.s (puprime): 572.760 velas M5 del 10/09/2018 al 30/10/2026; velas a las 17 h NY (pausa diaria): 0.
- DJ30.s (puprime): 572.854 velas M5 del 07/09/2018 al 30/10/2026; velas a las 17 h NY (pausa diaria): 0.
- USTEC (metaquotes): 292.855 velas M5 del 06/07/2022 al 30/10/2026; velas a las 17 h NY (pausa diaria): 1351.

## Veredicto

| Criterio | Valor | Cumple |
|---|---:|---:|
| R neto > 0 y t > 1.65 en al menos 2 de 3 | 1 de 3 | **no** |
| Los 3 juntos: R neto > 0 y t > 2.0 | +0.013 R, t +1.11 | **no** |

**No se confirma.**

## ORB principal (45 min, 09:00–09:45)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| SP500.s (puprime) | 2077 | 51.6 % | +0.001 | +1.5 | 1.00 | -29.7 | +0.04 |
| DJ30.s (puprime) | 2057 | 50.3 % | +0.003 | +6.9 | 1.01 | -37.9 | +0.19 |
| USTEC (metaquotes) | 1030 | 53.9 % | +0.057 | +58.4 | 1.17 | -17.5 | +2.23 |
| Los 3 juntos | 5164 | 51.5 % | +0.013 | +66.8 | 1.03 | -49.6 | +1.11 |

Sin costes (R bruto):

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| SP500.s (puprime) | 2077 | 52.0 % | +0.029 | +60.2 | 1.07 | -17.6 | +1.51 |
| DJ30.s (puprime) | 2057 | 50.8 % | +0.020 | +41.7 | 1.06 | -30.1 | +1.13 |
| USTEC (metaquotes) | 1030 | 54.4 % | +0.065 | +66.8 | 1.19 | -17.1 | +2.55 |
| Los 3 juntos | 5164 | 52.0 % | +0.033 | +168.7 | 1.09 | -42.4 | +2.80 |

Por lado:

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| SP500.s (puprime), long | 1065 | 54.7 % | +0.031 | +33.2 | 1.08 | -13.4 | +1.18 |
| SP500.s (puprime), short | 1012 | 48.2 % | -0.031 | -31.7 | 0.93 | -43.8 | -1.12 |
| DJ30.s (puprime), long | 1033 | 53.4 % | +0.025 | +25.5 | 1.07 | -20.2 | +0.99 |
| DJ30.s (puprime), short | 1024 | 47.1 % | -0.018 | -18.6 | 0.95 | -32.5 | -0.71 |
| USTEC (metaquotes), long | 546 | 59.5 % | +0.109 | +59.6 | 1.35 | -9.9 | +3.19 |
| USTEC (metaquotes), short | 484 | 47.5 % | -0.003 | -1.3 | 0.99 | -13.9 | -0.07 |

Por mitades del histórico:

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| SP500.s (puprime), 1.ª mitad | 1039 | 51.0 % | -0.017 | -17.9 | 0.96 | -29.7 | -0.64 |
| SP500.s (puprime), 2.ª mitad | 1038 | 52.1 % | +0.019 | +19.4 | 1.05 | -22.9 | +0.68 |
| DJ30.s (puprime), 1.ª mitad | 1029 | 51.5 % | -0.009 | -9.3 | 0.98 | -32.4 | -0.35 |
| DJ30.s (puprime), 2.ª mitad | 1028 | 49.0 % | +0.016 | +16.2 | 1.05 | -16.4 | +0.63 |
| USTEC (metaquotes), 1.ª mitad | 515 | 54.2 % | +0.087 | +44.6 | 1.26 | -9.7 | +2.37 |
| USTEC (metaquotes), 2.ª mitad | 515 | 53.6 % | +0.027 | +13.7 | 1.08 | -17.5 | +0.75 |

## Contexto: las otras duraciones que acaban a las 09:45 (no cuentan para el veredicto)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| SP500.s, 15 min (09:30–09:45) | 2089 | 51.0 % | -0.012 | -24.9 | 0.97 | -45.6 | -0.60 |
| SP500.s, 30 min (09:15–09:45) | 2083 | 51.2 % | -0.004 | -9.2 | 0.99 | -34.6 | -0.23 |
| SP500.s, 60 min (08:45–09:45) | 2072 | 52.1 % | +0.011 | +22.9 | 1.03 | -22.3 | +0.58 |
| DJ30.s, 15 min (09:30–09:45) | 2076 | 50.0 % | -0.007 | -14.0 | 0.98 | -42.4 | -0.36 |
| DJ30.s, 30 min (09:15–09:45) | 2065 | 50.7 % | +0.010 | +20.9 | 1.03 | -31.5 | +0.56 |
| DJ30.s, 60 min (08:45–09:45) | 2049 | 50.4 % | +0.009 | +18.0 | 1.03 | -34.7 | +0.50 |
| USTEC, 15 min (09:30–09:45) | 1038 | 52.5 % | +0.039 | +40.4 | 1.10 | -20.5 | +1.45 |
| USTEC, 30 min (09:15–09:45) | 1034 | 53.3 % | +0.053 | +54.3 | 1.15 | -17.6 | +2.02 |
| USTEC, 60 min (08:45–09:45) | 1021 | 54.2 % | +0.064 | +64.9 | 1.19 | -15.9 | +2.53 |
