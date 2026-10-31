# Backtest: TBR de 18:00 a 20:00 NY con EMA 20 (M15)

Script: `scripts/backtest_tbr.py`. Solo lee velas M15 ya descargadas.

## Estrategia y criterios (fijados antes de ver los resultados)

- **TBR:** máximo y mínimo de las velas M15 de 18:00 a 20:00 NY. Solo se opera si mide entre 100 y 300 puntos del NAS100.
- **Rotura con cuerpo:** la primera vela M15 que cierra fuera del TBR y del mismo lado de la EMA 20 (las roturas contra la EMA se ignoran y se sigue esperando). Tiene que cerrar como tarde a las 00:00 NY; si no, se cancela el día. Una operación por día.
- **Entrada** a la apertura de la vela siguiente; **stop** en el extremo contrario del TBR; **objetivo** 2R; a 1R el stop pasa a la entrada (BE). Stop y objetivo en la misma vela: cuenta el stop. Dentro del trade se sigue hasta el stop o el objetivo, aunque pase de día.
- **Costes:** spread real de MT5 en la vela de entrada.
- **Otros mercados:** el ancho se pasa a puntos del NAS100 con la relación de precios del día.
- **Se da por buena si:** (1) NAS100 de PUPrime, todo el histórico: ≥ 100 operaciones y R neto > +0.05 con t > 2.0; (2) R neto positivo en 2018-2022 y en 2023 en adelante; (3) R neto > 0 con t > 1.65 en al menos 2 de 3: SP500 y DJ30 de PUPrime, NAS100 de MetaQuotes.

## Veredicto

| Criterio | Valor | Cumple |
|---|---:|---:|
| NAS100.s (puprime): ≥ 100 ops, R neto > +0.05, t > 2.0 | 192 ops, +0.129 R, t +1.40 | **no** |
| Positivo en 2018-2022 y en 2023-2026 | +0.092 R, t +0.54 / +0.142 R, t +1.30 | sí |
| Otros mercados con R neto > 0 y t > 1.65 | 0 de 3 | **no** |

**No pasa.**

## Ancho del TBR en el NAS100 de PUPrime

2097 días. Mediana 39.0 puntos; percentil 10 15.8, percentil 90 114.1. Entre 100 y 300 puntos: 11.9 % de los días. Mediana por año: 2018 29, 2019 17, 2020 44, 2021 31, 2022 45, 2023 26, 2024 39, 2025 64, 2026 95.

Embudo: días con TBR 2097, ancho válido 250, con rotura 192, roturas contra la EMA ignoradas 30, operaciones 192.

## Resultados (R neto, con spread)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| NAS100.s (puprime), todo | 192 | 29.7 % | +0.129 | +24.8 | 1.28 | -9.3 | +1.40 |
|   2018-2022 | 50 | 26.0 % | +0.092 | +4.6 | 1.22 | -7.2 | +0.54 |
|   2023-2026 | 142 | 31.0 % | +0.142 | +20.2 | 1.30 | -8.2 | +1.30 |
|   sin costes (R bruto) | 192 | 29.7 % | +0.141 | +27.0 | 1.31 | -9.0 | +1.53 |
|   largos | 100 | 35.0 % | +0.258 | +25.8 | 1.59 | -5.1 | +1.94 |
|   cortos | 92 | 23.9 % | -0.011 | -1.0 | 0.98 | -14.7 | -0.09 |
| SP500.s (puprime) | 98 | 30.6 % | +0.169 | +16.6 | 1.39 | -7.6 | +1.31 |
| DJ30.s (puprime) | 59 | 30.5 % | +0.176 | +10.4 | 1.41 | -5.3 | +1.05 |
| USTEC (metaquotes) | 143 | 30.1 % | +0.099 | +14.1 | 1.20 | -12.4 | +0.90 |
| SP500.s (puprime) sin costes | 98 | 30.6 % | +0.184 | +18.0 | 1.43 | -7.0 | +1.42 |
| DJ30.s (puprime) sin costes | 59 | 30.5 % | +0.186 | +11.0 | 1.44 | -5.0 | +1.12 |
| USTEC (metaquotes) sin costes | 143 | 30.1 % | +0.105 | +15.0 | 1.21 | -12.0 | +0.96 |

Cómo terminan (NAS100 de PUPrime): stop 87, objetivo 57, BE 48. Coste medio 0.011 R.

Embudo de los otros mercados: SP500.s (puprime): días con TBR 2097, ancho válido 132, con rotura 98, roturas contra la EMA ignoradas 26, operaciones 98; DJ30.s (puprime): días con TBR 2094, ancho válido 87, con rotura 59, roturas contra la EMA ignoradas 20, operaciones 59; USTEC (metaquotes): días con TBR 1074, ancho válido 186, con rotura 143, roturas contra la EMA ignoradas 30, operaciones 143.

## Por año (NAS100 de PUPrime)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2019 | 1 | 100.0 % | +1.994 | +2.0 | - | -0.0 | +0.00 |
| 2020 | 24 | 29.2 % | +0.287 | +6.9 | 1.97 | -2.0 | +1.17 |
| 2021 | 9 | 22.2 % | -0.120 | -1.1 | 0.79 | -4.1 | -0.28 |
| 2022 | 16 | 18.8 % | -0.199 | -3.2 | 0.65 | -5.1 | -0.68 |
| 2023 | 3 | 0.0 % | -0.676 | -2.0 | 0.00 | -2.0 | -2.03 |
| 2024 | 15 | 46.7 % | +0.523 | +7.8 | 2.29 | -3.0 | +1.39 |
| 2025 | 39 | 28.2 % | +0.066 | +2.6 | 1.13 | -8.1 | +0.32 |
| 2026 | 85 | 30.6 % | +0.139 | +11.8 | 1.30 | -5.1 | +0.99 |

## Sensibilidad (no cuenta para el veredicto)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| sin filtro EMA: NAS100.s (puprime) | 194 | 28.9 % | +0.107 | +20.8 | 1.23 | -9.3 | +1.18 |
| sin filtro EMA: SP500.s (puprime) | 99 | 31.3 % | +0.177 | +17.6 | 1.40 | -7.5 | +1.37 |
| sin filtro EMA: DJ30.s (puprime) | 60 | 30.0 % | +0.139 | +8.3 | 1.30 | -6.3 | +0.84 |
| sin filtro EMA: USTEC (metaquotes) | 144 | 30.6 % | +0.105 | +15.1 | 1.21 | -12.4 | +0.96 |
| anular el día si la rotura va contra la EMA: NAS100.s (puprime) | 182 | 29.1 % | +0.120 | +21.9 | 1.26 | -8.3 | +1.28 |
| anular el día si la rotura va contra la EMA: SP500.s (puprime) | 92 | 30.4 % | +0.149 | +13.7 | 1.33 | -9.6 | +1.11 |
| anular el día si la rotura va contra la EMA: DJ30.s (puprime) | 56 | 28.6 % | +0.114 | +6.4 | 1.25 | -7.3 | +0.67 |
| anular el día si la rotura va contra la EMA: USTEC (metaquotes) | 136 | 30.1 % | +0.104 | +14.1 | 1.21 | -11.4 | +0.93 |
| sin BE: NAS100.s (puprime) | 192 | 37.5 % | +0.114 | +21.8 | 1.18 | -10.3 | +1.08 |
| sin BE: SP500.s (puprime) | 98 | 38.8 % | +0.149 | +14.6 | 1.24 | -15.1 | +1.00 |
| sin BE: DJ30.s (puprime) | 59 | 47.5 % | +0.413 | +24.4 | 1.78 | -7.2 | +2.10 |
| sin BE: USTEC (metaquotes) | 143 | 35.7 % | +0.064 | +9.1 | 1.10 | -12.5 | +0.53 |
| objetivo 1R (BE desactivado): NAS100.s (puprime) | 192 | 54.7 % | +0.082 | +15.8 | 1.18 | -7.2 | +1.14 |
| objetivo 1R (BE desactivado): SP500.s (puprime) | 98 | 57.1 % | +0.128 | +12.6 | 1.30 | -5.2 | +1.28 |
| objetivo 1R (BE desactivado): DJ30.s (puprime) | 59 | 57.6 % | +0.142 | +8.4 | 1.33 | -5.3 | +1.09 |
| objetivo 1R (BE desactivado): USTEC (metaquotes) | 143 | 50.3 % | +0.001 | +0.1 | 1.00 | -14.4 | +0.01 |
| sin filtro de ancho: NAS100.s (puprime) | 1758 | 24.7 % | -0.056 | -99.2 | 0.90 | -141.1 | -1.93 |
| sin filtro de ancho: SP500.s (puprime) | 1732 | 24.2 % | -0.088 | -151.7 | 0.84 | -151.7 | -2.99 |
| sin filtro de ancho: DJ30.s (puprime) | 1687 | 23.9 % | -0.089 | -150.4 | 0.84 | -171.0 | -3.01 |
| sin filtro de ancho: USTEC (metaquotes) | 854 | 26.1 % | -0.030 | -26.0 | 0.94 | -67.9 | -0.71 |
