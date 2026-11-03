# CRT por zona común: resultados del backtest (03/11/2026)

`scripts/backtest_crt_zona.py`, velas M5 de PUPrime (dic. 2023 - oct. 2026, 200 000 velas por mercado), mismo motor que la skill. Una operación a la vez por mercado, entrada a la apertura de la vela siguiente al cierre sobre el CISD, stop en el extremo del sweep. Neto = bruto menos un spread supuesto (índices 1,5 pb, forex 0,7 pb).

| Variante (PUPrime) | n | R bruto | R neto | IC95 neto |
|---|---|---|---|---|
| 2R, BE a 1R (la del bot) | 5 055 | -0,015 | -0,111 | -0,14..-0,08 |
| 2R, sin BE | 4 954 | -0,023 | -0,120 | -0,15..-0,08 |
| 1R, BE a 1R | 5 237 | -0,017 | -0,114 | -0,14..-0,09 |
| 3R, BE a 1R | 4 930 | -0,009 | -0,106 | -0,14..-0,07 |
| 3R, sin BE | 4 775 | -0,027 | -0,124 | -0,17..-0,08 |
| 2R, BE a 1R (MetaQuotes) | 5 067 | -0,028 | -0,129 | -0,16..-0,10 |

La variante del bot (2R, BE a 1R) por mercado: NAS100 -0,093, SP500 -0,156, DJ30 -0,080, EURUSD -0,121, GBPUSD -0,101 R netos; largos -0,100 y cortos -0,121. Primer 60 % del tiempo -0,114 y último 40 % -0,106.

**Conclusión: sin ventaja.** El bruto es cero en todos los mercados, lados, periodos y objetivos probados, y el spread lo deja en negativo. El perfil CRT sirve para forwardtest en simulación, como hasta ahora.

**Setup OK sin Entrada** (la zona común existe pero el precio sigue sin tocarla): NAS100 1 299, SP500 1 200, DJ30 1 310, EURUSD 665 y GBPUSD 697 veces en el mismo periodo, frente a 1 031, 1 038, 957, 1 313 y 1 272 setups con CISD. Son marcas del gráfico, no operaciones.
