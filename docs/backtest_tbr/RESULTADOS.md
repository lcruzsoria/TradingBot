# Backtest: TBR de 18:00 a 20:00 NY con EMA 20 (M15)

Script: `scripts/backtest_tbr.py`. Solo lee velas M15 ya descargadas.

## Estrategia y criterios (fijados antes de ver los resultados)

- **TBR:** máximo y mínimo de las velas M15 de 18:00 a 20:00 NY. Solo se opera si mide entre 100 y 300 pips del NAS100 (de 10 a 30 puntos).
- **Rotura con cuerpo:** la primera vela M15 que cierra fuera del TBR y del mismo lado de la EMA 20 (las roturas contra la EMA se ignoran y se sigue esperando). Tiene que cerrar como tarde a las 00:00 NY; si no, se cancela el día. Una operación por día.
- **Entrada** a la apertura de la vela siguiente; **stop** en el extremo contrario del TBR; **objetivo** 2R; a 1R el stop pasa a la entrada (BE). Stop y objetivo en la misma vela: cuenta el stop. Dentro del trade se sigue hasta el stop o el objetivo, aunque pase de día.
- **Costes:** spread real de MT5 en la vela de entrada.
- **Otros mercados:** el ancho se pasa a puntos del NAS100 con la relación de precios del día.
- **Se da por buena si:** (1) NAS100 de PUPrime, todo el histórico: ≥ 100 operaciones y R neto > +0.05 con t > 2.0; (2) R neto positivo en 2018-2022 y en 2023 en adelante; (3) R neto > 0 con t > 1.65 en al menos 2 de 3: SP500 y DJ30 de PUPrime, NAS100 de MetaQuotes.

## Veredicto

| Criterio | Valor | Cumple |
|---|---:|---:|
| NAS100.s (puprime): ≥ 100 ops, R neto > +0.05, t > 2.0 | 638 ops, -0.096 R, t -1.99 | **no** |
| Positivo en 2018-2022 y en 2023-2026 | -0.105 R, t -1.75 / -0.081 R, t -0.98 | **no** |
| Otros mercados con R neto > 0 y t > 1.65 | 0 de 3 | **no** |

**No pasa.**

## Ancho del TBR en el NAS100 de PUPrime

2097 días. Mediana 39.0 puntos; percentil 10 15.8, percentil 90 114.1. Entre 10 y 30 puntos: 33.7 % de los días. Mediana por año: 2018 29, 2019 17, 2020 44, 2021 31, 2022 45, 2023 26, 2024 39, 2025 64, 2026 95.

Embudo: días con TBR 2097, ancho válido 706, con rotura 638, roturas contra la EMA ignoradas 150, operaciones 638.

## Resultados (R neto, con spread)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| NAS100.s (puprime), todo | 638 | 24.1 % | -0.096 | -61.5 | 0.83 | -71.5 | -1.99 |
|   2018-2022 | 411 | 23.4 % | -0.105 | -43.0 | 0.81 | -59.5 | -1.75 |
|   2023-2026 | 227 | 25.6 % | -0.081 | -18.5 | 0.86 | -23.2 | -0.98 |
|   sin costes (R bruto) | 638 | 24.1 % | -0.041 | -26.0 | 0.92 | -45.0 | -0.84 |
|   largos | 354 | 24.6 % | -0.065 | -22.9 | 0.88 | -36.0 | -1.00 |
|   cortos | 284 | 23.6 % | -0.136 | -38.6 | 0.77 | -45.5 | -1.87 |
| SP500.s (puprime) | 799 | 25.2 % | -0.093 | -74.5 | 0.84 | -77.2 | -2.13 |
| DJ30.s (puprime) | 889 | 22.2 % | -0.169 | -150.6 | 0.72 | -167.6 | -4.22 |
| USTEC (metaquotes) | 260 | 26.5 % | -0.053 | -13.7 | 0.91 | -28.2 | -0.68 |
| SP500.s (puprime) sin costes | 799 | 25.2 % | -0.021 | -17.0 | 0.96 | -43.0 | -0.49 |
| DJ30.s (puprime) sin costes | 889 | 22.2 % | -0.112 | -100.0 | 0.80 | -121.0 | -2.80 |
| USTEC (metaquotes) sin costes | 260 | 26.5 % | +0.015 | +4.0 | 1.03 | -17.0 | +0.20 |

Cómo terminan (NAS100 de PUPrime): stop 334, objetivo 154, BE 150. Coste medio 0.056 R.

Embudo de los otros mercados: SP500.s (puprime): días con TBR 2097, ancho válido 932, con rotura 799, roturas contra la EMA ignoradas 198, operaciones 799; DJ30.s (puprime): días con TBR 2094, ancho válido 1053, con rotura 889, roturas contra la EMA ignoradas 190, operaciones 889; USTEC (metaquotes): días con TBR 1074, ancho válido 294, con rotura 260, roturas contra la EMA ignoradas 84, operaciones 260.

## Por año (NAS100 de PUPrime)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2018 | 29 | 20.7 % | -0.045 | -1.3 | 0.90 | -6.8 | -0.21 |
| 2019 | 152 | 23.0 % | -0.113 | -17.2 | 0.80 | -23.8 | -1.16 |
| 2020 | 58 | 25.9 % | -0.087 | -5.1 | 0.85 | -15.4 | -0.52 |
| 2021 | 115 | 20.9 % | -0.197 | -22.6 | 0.67 | -34.8 | -1.79 |
| 2022 | 57 | 28.1 % | +0.057 | +3.2 | 1.12 | -9.9 | +0.34 |
| 2023 | 132 | 22.7 % | -0.097 | -12.8 | 0.82 | -21.1 | -0.94 |
| 2024 | 62 | 30.6 % | +0.002 | +0.1 | 1.00 | -14.9 | +0.01 |
| 2025 | 30 | 26.7 % | -0.188 | -5.6 | 0.73 | -10.5 | -0.77 |
| 2026 | 3 | 33.3 % | -0.051 | -0.2 | 0.93 | -2.1 | -0.05 |

## Sensibilidad (no cuenta para el veredicto)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| sin filtro EMA: NAS100.s (puprime) | 643 | 24.0 % | -0.100 | -64.5 | 0.82 | -74.5 | -2.09 |
| sin filtro EMA: SP500.s (puprime) | 813 | 24.7 % | -0.109 | -88.8 | 0.81 | -91.4 | -2.52 |
| sin filtro EMA: DJ30.s (puprime) | 903 | 21.2 % | -0.192 | -173.3 | 0.68 | -189.5 | -4.89 |
| sin filtro EMA: USTEC (metaquotes) | 264 | 25.8 % | -0.077 | -20.4 | 0.87 | -34.6 | -1.00 |
| anular el día si la rotura va contra la EMA: NAS100.s (puprime) | 583 | 23.8 % | -0.101 | -58.6 | 0.82 | -69.1 | -2.00 |
| anular el día si la rotura va contra la EMA: SP500.s (puprime) | 743 | 24.9 % | -0.096 | -71.7 | 0.83 | -74.4 | -2.13 |
| anular el día si la rotura va contra la EMA: DJ30.s (puprime) | 822 | 22.0 % | -0.168 | -137.9 | 0.72 | -158.2 | -4.03 |
| anular el día si la rotura va contra la EMA: USTEC (metaquotes) | 233 | 25.3 % | -0.086 | -20.0 | 0.85 | -29.1 | -1.05 |
| sin BE: NAS100.s (puprime) | 638 | 31.2 % | -0.120 | -76.5 | 0.84 | -90.3 | -2.17 |
| sin BE: SP500.s (puprime) | 799 | 33.5 % | -0.066 | -52.5 | 0.91 | -78.9 | -1.31 |
| sin BE: DJ30.s (puprime) | 889 | 30.5 % | -0.142 | -126.6 | 0.81 | -151.2 | -3.07 |
| sin BE: USTEC (metaquotes) | 260 | 32.3 % | -0.099 | -25.7 | 0.86 | -36.9 | -1.13 |
| objetivo 1R (BE desactivado): NAS100.s (puprime) | 638 | 47.6 % | -0.103 | -65.5 | 0.81 | -74.8 | -2.59 |
| objetivo 1R (BE desactivado): SP500.s (puprime) | 799 | 47.6 % | -0.121 | -96.5 | 0.79 | -104.5 | -3.42 |
| objetivo 1R (BE desactivado): DJ30.s (puprime) | 889 | 44.4 % | -0.168 | -149.6 | 0.71 | -158.8 | -5.04 |
| objetivo 1R (BE desactivado): USTEC (metaquotes) | 260 | 48.5 % | -0.099 | -25.7 | 0.82 | -30.1 | -1.59 |
| sin filtro de ancho: NAS100.s (puprime) | 1758 | 24.7 % | -0.056 | -99.2 | 0.90 | -141.1 | -1.93 |
| sin filtro de ancho: SP500.s (puprime) | 1732 | 24.2 % | -0.088 | -151.7 | 0.84 | -151.7 | -2.99 |
| sin filtro de ancho: DJ30.s (puprime) | 1687 | 23.9 % | -0.089 | -150.4 | 0.84 | -171.0 | -3.01 |
| sin filtro de ancho: USTEC (metaquotes) | 854 | 26.1 % | -0.030 | -26.0 | 0.94 | -67.9 | -0.71 |
