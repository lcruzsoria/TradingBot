# Backtest: CRT (variante B) en NAS100, H3 → M15/M30/H1 → M1 · esperando al cierre de C2

**Variante sin look-ahead:** C2 tiene que haber cerrado dentro del rango de C1 (cierre real del HTF) y el CISD y la entrada se buscan desde el cierre de C2 hasta el final de C3. Si el precio supera el extremo del sweep en C3, el setup se anula.

Script: `scripts/backtest_crt.py`. Solo lee velas M1, M3 y M5 descargadas de MT5. Las reglas y definiciones operativas están en la cabecera del script y en `GUIA.md`; se fijaron antes de ver los resultados.

- **Se da por buena (cada combinación LTF × entrada) si:** (1) NAS100 de PUPrime, todo el histórico: ≥ 100 operaciones y R neto > +0.05 con t > 2.0; (2) R neto positivo en los dos periodos (1.ª mitad (hasta 2025-06); 2.ª mitad (desde 2025-06)); (3) R neto > 0 en el control (NAS100 (USTEC) de MetaQuotes).
- Son 3 combinaciones, así que algún t alto por azar es esperable: se mira la consistencia, no un solo número.

## Veredicto

| Combinación | NAS100 de PUPrime | (1) | 1.ª mitad (hasta 2025-06) / 2.ª mitad (desde 2025-06) | (2) | Control: NAS100 (USTEC) de MetaQuotes | (3) | Resultado |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 139 ops, -0.212 R, t -2.32 | **no** | -0.185 R, t -1.29 / -0.238 R, t -2.04 | **no** | -0.208 R, t -2.37 | **no** | No pasa |
| M1 · 2. retesteo del iFVG | 21 ops, -0.004 R, t -0.01 | **no** | -0.301 R, t -0.85 / +0.323 R, t +0.73 | **no** | -0.264 R, t -1.12 | **no** | No pasa |
| M1 · 3. primera vela sin mecha | 132 ops, -0.044 R, t -0.44 | **no** | -0.014 R, t -0.09 / -0.072 R, t -0.56 | **no** | -0.133 R, t -1.44 | **no** | No pasa |

**0 de 3 combinaciones pasan.**

## Datos

- NAS100.s (puprime) M1: 999999 velas, 2024-01-04 → 2026-10-30 (NY).
- NAS100.s (puprime) M5: 573135 velas, 2018-09-10 → 2026-10-30 (NY).
- USTEC (metaquotes) M1: 999999 velas, 2023-10-30 → 2026-10-30 (NY).
- USTEC (metaquotes) M5: 292870 velas, 2022-07-06 → 2026-10-30 (NY).

## Embudo (cuántos pasos pasan)

| Mercado | velas HTF con sweep | con FVG de MTF sin mitigar al alcance | con el extremo tocando el FVG | con iFVG | con CISD | setups finales |
|---|---:|---:|---:|---:|---:|---:|
| NAS100.s (puprime) M1 | 2184 | 423 | 347 | 255 | 140 | 140 |
| USTEC (metaquotes) M1 | 2048 | 404 | 327 | 231 | 142 | 142 |

## Resultados en NAS100 de PUPrime (R neto, con spread)

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 139 | 20.1 % | -0.212 | -29.5 | 0.62 | -29.5 | -2.32 |
|   1.ª mitad (hasta 2025-06) | 67 | 22.4 % | -0.185 | -12.4 | 0.69 | -21.3 | -1.29 |
|   2.ª mitad (desde 2025-06) | 72 | 18.1 % | -0.238 | -17.1 | 0.54 | -22.1 | -2.04 |
|   sin costes (R bruto) | 139 | 20.1 % | -0.175 | -24.3 | 0.67 | -24.3 | -1.92 |
|   largos | 75 | 17.3 % | -0.258 | -19.3 | 0.52 | -19.3 | -2.25 |
|   cortos | 64 | 23.4 % | -0.159 | -10.2 | 0.73 | -12.2 | -1.08 |
| M1 · 2. retesteo del iFVG | 21 | 28.6 % | -0.004 | -0.1 | 0.99 | -5.9 | -0.01 |
|   1.ª mitad (hasta 2025-06) | 11 | 18.2 % | -0.301 | -3.3 | 0.54 | -5.9 | -0.85 |
|   2.ª mitad (desde 2025-06) | 10 | 40.0 % | +0.323 | +3.2 | 1.75 | -4.3 | +0.73 |
|   sin costes (R bruto) | 21 | 28.6 % | +0.095 | +2.0 | 1.20 | -5.0 | +0.34 |
|   largos | 13 | 30.8 % | +0.124 | +1.6 | 1.27 | -4.9 | +0.34 |
|   cortos | 8 | 25.0 % | -0.211 | -1.7 | 0.69 | -3.3 | -0.44 |
| M1 · 3. primera vela sin mecha | 132 | 30.3 % | -0.044 | -5.9 | 0.91 | -15.3 | -0.44 |
|   1.ª mitad (hasta 2025-06) | 63 | 33.3 % | -0.014 | -0.9 | 0.98 | -15.1 | -0.09 |
|   2.ª mitad (desde 2025-06) | 69 | 27.5 % | -0.072 | -5.0 | 0.84 | -15.3 | -0.56 |
|   sin costes (R bruto) | 132 | 30.3 % | -0.002 | -0.2 | 1.00 | -13.9 | -0.02 |
|   largos | 72 | 27.8 % | -0.086 | -6.2 | 0.82 | -9.6 | -0.68 |
|   cortos | 60 | 33.3 % | +0.006 | +0.4 | 1.01 | -7.5 | +0.04 |

## Control: NAS100 (USTEC) de MetaQuotes

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| M1 · 1. vela siguiente al CISD | 142 | 21.1 % | -0.208 | -29.6 | 0.61 | -31.5 | -2.37 |
|   1.ª mitad (hasta 2025-06) | 68 | 26.5 % | -0.161 | -10.9 | 0.71 | -14.1 | -1.18 |
|   2.ª mitad (desde 2025-06) | 74 | 16.2 % | -0.252 | -18.6 | 0.52 | -22.6 | -2.21 |
| M1 · 2. retesteo del iFVG | 20 | 15.0 % | -0.264 | -5.3 | 0.53 | -5.3 | -1.12 |
|   1.ª mitad (hasta 2025-06) | 10 | 10.0 % | -0.286 | -2.9 | 0.41 | -3.7 | -0.98 |
|   2.ª mitad (desde 2025-06) | 10 | 20.0 % | -0.242 | -2.4 | 0.62 | -5.1 | -0.63 |
| M1 · 3. primera vela sin mecha | 137 | 25.5 % | -0.133 | -18.2 | 0.74 | -19.9 | -1.44 |
|   1.ª mitad (hasta 2025-06) | 64 | 31.2 % | -0.068 | -4.3 | 0.87 | -9.0 | -0.47 |
|   2.ª mitad (desde 2025-06) | 73 | 20.5 % | -0.190 | -13.8 | 0.62 | -17.5 | -1.60 |

## Cómo terminan y riesgo (NAS100 de PUPrime)

| Combinación | Cierres | Riesgo mediano (pts) | p10 | p90 | Coste medio (R) | Coste > 0,2 R |
|---|---:|---:|---:|---:|---:|---:|
| M1 · 1 | stop 68, BE 29, objetivo 22, sesión 20 | 64.0 | 23.2 | 166.0 | 0.037 | 0 % |
| M1 · 2 | stop 10, objetivo 6, BE 5 | 19.0 | 10.5 | 60.0 | 0.099 | 5 % |
| M1 · 3 | stop 58, sesión 28, objetivo 26, BE 20 | 60.1 | 18.6 | 184.6 | 0.043 | 1 % |

## Por año (NAS100 de PUPrime)

**M1 · 1. vela siguiente al CISD**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 43 | 18.6 % | -0.349 | -15.0 | 0.49 | -21.3 | -2.04 |
| 2025 | 58 | 29.3 % | +0.094 | +5.5 | 1.25 | -4.5 | +0.64 |
| 2026 | 38 | 7.9 % | -0.525 | -20.0 | 0.23 | -20.0 | -3.81 |

**M1 · 2. retesteo del iFVG**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 10 | 20.0 % | -0.321 | -3.2 | 0.54 | -5.9 | -0.82 |
| 2025 | 6 | 66.7 % | +1.234 | +7.4 | 47.31 | -0.2 | +2.97 |
| 2026 | 5 | 0.0 % | -0.856 | -4.3 | 0.00 | -4.3 | -4.26 |

**M1 · 3. primera vela sin mecha**

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 40 | 25.0 % | -0.241 | -9.6 | 0.63 | -15.1 | -1.29 |
| 2025 | 57 | 43.9 % | +0.286 | +16.3 | 1.82 | -3.2 | +1.81 |
| 2026 | 35 | 14.3 % | -0.358 | -12.5 | 0.41 | -12.5 | -2.18 |

## Sensibilidad (no cuenta para el veredicto)

Cada fila vuelve a buscar los setups con el cambio indicado. «C2 cierra dentro» usa información futura (el cierre de C2).

|  | Ops | Acierto | R medio | R total | PF | Máx. DD | t |
|---|---:|---:|---:|---:|---:|---:|---:|
| antigüedad del FVG 3 días: M1 · 1 | 120 | 17.5 % | -0.277 | -33.3 | 0.52 | -33.3 | -2.93 |
| antigüedad del FVG 3 días: M1 · 2 | 18 | 27.8 % | -0.043 | -0.8 | 0.92 | -5.9 | -0.14 |
| antigüedad del FVG 3 días: M1 · 3 | 113 | 28.3 % | -0.085 | -9.6 | 0.84 | -16.6 | -0.79 |
| antigüedad del FVG 30 días: M1 · 1 | 152 | 21.7 % | -0.190 | -28.9 | 0.65 | -30.9 | -2.18 |
| antigüedad del FVG 30 días: M1 · 2 | 23 | 30.4 % | +0.008 | +0.2 | 1.02 | -5.9 | +0.03 |
| antigüedad del FVG 30 días: M1 · 3 | 145 | 30.3 % | -0.047 | -6.8 | 0.90 | -16.3 | -0.50 |
| tolerancia al tocar el FVG 0,05 % del precio: M1 · 1 | 358 | 24.0 % | -0.165 | -59.1 | 0.70 | -61.7 | -2.81 |
| tolerancia al tocar el FVG 0,05 % del precio: M1 · 2 | 68 | 23.5 % | -0.279 | -19.0 | 0.60 | -20.6 | -1.90 |
| tolerancia al tocar el FVG 0,05 % del precio: M1 · 3 | 335 | 28.7 % | -0.103 | -34.4 | 0.80 | -34.5 | -1.67 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 1 | 139 | 20.1 % | -0.212 | -29.5 | 0.62 | -29.5 | -2.32 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 2 | 21 | 28.6 % | -0.004 | -0.1 | 0.99 | -5.9 | -0.01 |
| exigir que C2 cierre dentro de C1 (look-ahead): M1 · 3 | 132 | 30.3 % | -0.044 | -5.9 | 0.91 | -15.3 | -0.44 |
| sin BE: M1 · 1 | 139 | 29.5 % | -0.150 | -20.8 | 0.77 | -20.8 | -1.38 |
| sin BE: M1 · 2 | 21 | 33.3 % | -0.058 | -1.2 | 0.92 | -7.9 | -0.19 |
| sin BE: M1 · 3 | 132 | 34.8 % | -0.059 | -7.9 | 0.90 | -17.1 | -0.53 |
| objetivo 3R: M1 · 1 | 139 | 18.7 % | -0.136 | -18.9 | 0.76 | -24.2 | -1.24 |
| objetivo 3R: M1 · 2 | 32 | 12.5 % | -0.229 | -7.3 | 0.61 | -8.4 | -1.00 |
| objetivo 3R: M1 · 3 | 131 | 23.7 % | -0.067 | -8.8 | 0.87 | -18.8 | -0.59 |
