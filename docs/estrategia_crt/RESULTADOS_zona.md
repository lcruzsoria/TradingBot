# CRT por zona común: resultados del backtest (03/11/2026)

`scripts/backtest_crt_zona.py`, velas M5 de PUPrime (dic. 2023 - oct. 2026, 200 000 velas por mercado), con el mismo motor que la skill y la regla final (iFVG invertido, pullback a la zona común, cierre con cuerpo sobre el CISD, FVG de M15 o M5 con iFVG de TF igual o menor, manda el de mayor TF). Una operación a la vez por mercado, entrada a la apertura de la vela siguiente, stop en el extremo del sweep. Neto = bruto menos un spread supuesto (índices 1,5 pb, forex 0,7 pb): los parquet no traen el spread.

| Variante (PUPrime) | n | R bruto | R neto | IC95 neto |
|---|---|---|---|---|
| 2R, BE a +1R (la del bot) | 4 729 | +0,050 | -0,048 | -0,08..-0,02 |
| 2R, sin BE | 4 619 | +0,037 | -0,061 | -0,10..-0,02 |
| 1R, BE a +1R | 4 922 | +0,031 | -0,067 | -0,09..-0,04 |
| 3R, BE a +1R | 4 600 | +0,059 | -0,039 | -0,08..-0,00 |
| 2R, BE a +1R (MetaQuotes) | 4 583 | +0,028 | -0,071 | -0,10..-0,04 |

La variante del bot (2R, BE a +1R) por mercado, R neto: NAS100 -0,031, SP500 -0,016, DJ30 -0,032, EURUSD -0,083, GBPUSD -0,057; largos -0,030 y cortos -0,066. Primer 60 % del tiempo -0,063 y último 40 % -0,025. El bruto es positivo en todos los mercados y periodos (+0,01 a +0,10 R) pero no cubre el spread.

Embudo (variante del bot), NAS100: 4 686 velas con sweep, 3 756 con doble FVG y zona común, 1 417 con pullback a la zona, 893 con cierre sobre el CISD y 368 invalidadas.

**Setup OK sin Entrada** (zona común, iFVG invertido y el precio sigue sin volver a ella): NAS100 1 018, SP500 946, DJ30 984, EURUSD 611 y GBPUSD 652 veces en el mismo periodo. Son marcas del gráfico, no operaciones.

**Historia de la regla** (misma variante 2R, BE +1R, PUPrime; R bruto / neto):
- Sin exigir que el iFVG se invierta antes del pullback y solo con FVG de M15: 5 055 operaciones, -0,015 / -0,111.
- Con el iFVG invertido antes del pullback y solo con FVG de M15: 3 358 operaciones, -0,002 / -0,094.
- Regla final, con FVG de M15 o de M5: 4 729 operaciones, +0,050 / -0,048.

**Conclusión: no hay ventaja neta.** Con la regla final el bruto es ligeramente positivo, pero el spread supuesto lo deja en negativo en todas las variantes probadas (solo SP500 con objetivo 3R queda en +0,006 R neto, con un intervalo de -0,09 a +0,10). El perfil CRT sirve para forwardtest en simulación, como hasta ahora.
