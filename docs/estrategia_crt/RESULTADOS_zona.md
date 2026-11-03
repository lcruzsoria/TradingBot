# CRT por zona común: resultados del backtest (03/11/2026)

`scripts/backtest_crt_zona.py`, velas M5 de PUPrime (dic. 2023 - oct. 2026, 200 000 velas por mercado), con el mismo motor que la skill y la regla final (iFVG invertido, pullback a la zona común, cierre con cuerpo sobre el CISD, FVG de M15 o M5 con iFVG de TF igual o menor, manda el de mayor TF). Una operación a la vez por mercado, entrada a la apertura de la vela siguiente, stop en el extremo del sweep. Neto = bruto menos un spread supuesto (índices 1,5 pb, forex 0,7 pb): los parquet no traen el spread.

**Actualización (03/11/2026, tarde): el primer hueco es siempre el iFVG y sigue activo.** Regla final: el primer hueco en nacer es el iFVG (el que se invierte y da el CISD); tiene que seguir activo (sin cerrarse del todo con mecha o cuerpo, ni invertirse) hasta que se forma el FVG normal, que nace después. El retest que cierra con cuerpo al otro lado de la zona invalida la pareja. Backtest rehecho con velas M5 y M15 de PUPrime recién descargadas (ene. 2024 - 03/11/2026) y el mismo motor que el bot. **Las tablas de abajo son de reglas anteriores y están desfasadas.**

| Variante (PUPrime, regla final) | n | R bruto | R neto | IC95 neto |
|---|---|---|---|---|
| 2R, BE a +1R (la del bot) | 2 201 | +0,014 | -0,074 | -0,12..-0,03 |
| 2R, sin BE | 2 181 | +0,007 | -0,081 | -0,13..-0,03 |
| 1R, BE a +1R | 2 244 | +0,025 | -0,063 | -0,10..-0,02 |
| 3R, BE a +1R | 2 169 | +0,026 | -0,062 | -0,12..-0,01 |

Por mercado (2R, BE +1R), R neto: NAS100 -0,107, SP500 -0,036, DJ30 -0,034, EURUSD -0,115, GBPUSD -0,064; largos -0,064 y cortos -0,084. Con las mismas velas la primera regla daba 3 366 operaciones, +0,049 bruto y -0,045 neto, y la regla anterior a esta 2 355 y -0,075: **cada regla quita operaciones y el resultado no mejora**. Por combinación: FVG M15 + iFVG M5 2 186 operaciones (-0,076 R neto), FVG M5 + iFVG M5 solo 16 y FVG M15 + iFVG M15 1 (el FVG de M5 casi nunca nace después del iFVG de M5 sin cerrarlo). **Sigue sin haber ventaja neta.**

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

## Todas las combinaciones de TF (03/11/2026)

`scripts/backtest_crt_combinaciones.py`: FVG e iFVG de 15, 5 o 3 min con TF del FVG ≥ TF del iFVG, cada combinación con las velas del TF de su iFVG (CISD y entrada de ese TF). Velas de PUPrime de 3, 5 y 15 min (tramo común: desde feb.-mar. de 2025 hasta el 03/11/2026, unos 20 meses), 2R, BE a +1R, spread supuesto como arriba. Cada combinación se simula por separado (una operación a la vez por mercado y combinación); «todas» es lo que haría el bot con todas a la vez (primer cierre sobre el CISD de cada C2 y lado, una posición por mercado).

| Combinación | n | R bruto | R neto | IC95 neto |
|---|---|---|---|---|
| FVG M15 + iFVG M15 | 16 | -0,164 | -0,214 | -0,77..+0,34 |
| FVG M15 + iFVG M5 | 1 400 | +0,010 | -0,075 | -0,13..-0,02 |
| FVG M15 + iFVG M3 | 1 225 | -0,004 | -0,102 | -0,17..-0,04 |
| FVG M5 + iFVG M5 | 741 | +0,143 | +0,041 | -0,04..+0,13 |
| FVG M5 + iFVG M3 | 4 422 | -0,045 | -0,165 | -0,20..-0,13 |
| FVG M3 + iFVG M3 | 732 | -0,031 | -0,164 | -0,25..-0,08 |
| **todas (el bot)** | 6 282 | -0,034 | -0,150 | -0,18..-0,12 |

- **Las combinaciones con iFVG de 3 min empeoran el conjunto:** son las que más setups dan (FVG M5 + iFVG M3: 4 422) y las que peor salen, porque sus stops son cortos y el spread pesa más; además, como entran antes que las de 5 o 15 min, «todas» se queda con ellas.
- **FVG M5 + iFVG M5 es la única con bruto claro (+0,143 R) y neto positivo (+0,041 R), pero con un intervalo de -0,04 a +0,13:** no es concluyente.
- **iFVG de 15 min:** solo 16 operaciones; con tan pocas no se puede decir nada.
- **Sesgo CRT:** con «todas», 0 a 3 puntos dan -0,128, -0,160, -0,169 y -0,127 R netos: tampoco ordena.
- **Conclusión:** añadir las combinaciones de 3 min empeora el resultado respecto a quedarse con las de 5 y 15 (≈ -0,04 R neto en el tramo largo). No hay ventaja neta con ninguna combinación salvo, sin significación, FVG M5 + iFVG M5.
