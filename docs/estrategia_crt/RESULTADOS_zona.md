# CRT por zona común: resultados del backtest (03/11/2026)

`scripts/backtest_crt_zona.py`, velas M5 de PUPrime (dic. 2023 - oct. 2026, 200 000 velas por mercado), con el mismo motor que la skill y la regla final (iFVG invertido, pullback a la zona común, cierre con cuerpo sobre el CISD, FVG de M15 o M5 con iFVG de TF igual o menor, manda el de mayor TF). Una operación a la vez por mercado, entrada a la apertura de la vela siguiente, stop en el extremo del sweep. Neto = bruto menos un spread supuesto (índices 1,5 pb, forex 0,7 pb): los parquet no traen el spread.

| Variante (PUPrime) | n | R bruto | R neto | IC95 neto |
|---|---|---|---|---|
| 2R, BE a +1R (la del bot) | 3 344 | +0,054 | -0,041 | -0,08..-0,00 |
| 2R, sin BE | 3 290 | +0,054 | -0,041 | -0,08..+0,00 |
| 1R, BE a +1R | 3 448 | +0,041 | -0,054 | -0,09..-0,02 |
| 3R, BE a +1R | 3 268 | +0,077 | -0,019 | -0,06..+0,03 |
| 2R, BE a +1R (MetaQuotes) | 3 258 | +0,021 | -0,076 | -0,11..-0,04 |

(Regla final, con el retest que cierra con cuerpo bajo la zona invalidando la pareja y el estado propio de cada pareja iFVG + FVG: ver «Historia de la regla».)

La variante del bot (2R, BE a +1R) por mercado, R neto: NAS100 -0,068, SP500 -0,070, DJ30 +0,021, EURUSD -0,080, GBPUSD -0,008; largos -0,018 y cortos -0,063. Último 40 % del tiempo -0,020. Por puntos del sesgo CRT (0 a 3): -0,021, -0,067, -0,040 y -0,023 R netos: el sesgo no ordena los resultados.

Embudo (variante del bot), NAS100: 4 686 velas con sweep, 3 756 con doble FVG y zona común, 1 802 con pullback a la zona, 600 con cierre sobre el CISD (tras invalidar las parejas cuyo retest cierra bajo la zona) y 400 invalidadas.

**Setup OK sin Entrada** (zona común, iFVG invertido y el precio sigue sin volver a ella): NAS100 633 veces en el periodo (las demás, del mismo orden). Son marcas del gráfico, no operaciones.

**Historia de la regla** (misma variante 2R, BE +1R, PUPrime; R bruto / neto):
- Sin exigir que el iFVG se invierta antes del pullback y solo con FVG de M15: 5 055 operaciones, -0,015 / -0,111.
- Con el iFVG invertido antes del pullback y solo con FVG de M15: 3 358 operaciones, -0,002 / -0,094.
- Con FVG de M15 o de M5: 4 729 operaciones, +0,050 / -0,048.
- **Regla final (03/11/2026):** un retest que cierra con cuerpo bajo la zona invalida la pareja y cada pareja iFVG + FVG lleva su propio estado: 3 344 operaciones, +0,054 / -0,041. Se quitaron 1 385 entradas que la regla anterior daba por buenas.

**Conclusión: no hay ventaja neta.** Con la regla final el bruto es ligeramente positivo (+0,054 R) pero el spread supuesto lo deja en negativo en todas las variantes probadas, salvo DJ30 (+0,021 R neto, con un intervalo de -0,08 a +0,12). El perfil CRT sirve para forwardtest en simulación, como hasta ahora.
