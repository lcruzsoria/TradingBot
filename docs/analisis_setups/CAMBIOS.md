# Análisis histórico de los setups: cambios entre versiones

Registro de cada iteración de la estrategia de continuación sobre las TBR. Cada versión se calcula con **los mismos datos** y
tiene su Excel (`analisis/analisis_setups_vN.xlsx`, generado por `scripts/analisis_setups.py`; la carpeta `analisis/` no se sube
a git). Cada Excel incluye las hojas **Cambios** (qué cambia y por qué) y **Comparativa** (todas las versiones, por TBR y por sesgo).

## Datos y método (iguales en todas las versiones)

> **Actualización (16 oct 2026):** al añadir la v6 se volvieron a descargar las velas, que ya incluyen una semana más. Las cifras
> de v1–v5 varían en milésimas respecto a la primera pasada (p. ej. v1 pasó de −0,106R a −0,105R). La tabla resumen lleva ya
> las cifras actualizadas; las secciones de cada versión conservan las de la primera pasada.

- Velas M15 de MT5 (Vantage demo), ~100.000 por mercado (≈ oct 2022 – oct 2026): NAS100.r, SP500.r, DJ30.r, EURUSD, GBPUSD, XAUUSD.
- Hora de Nueva York (servidor = NY + 7 h). Día de trading desde las 18:00 NY en índices USA y 17:00 en el resto.
- Setup: toma de liquidez del High/Low de la TBR, retest del 50 % y segunda ruptura (la skill Setup, `detect`). Se invalida si toma
  el lado contrario; ventana de 24 h para completar el setup y 48 h para resolver la operación.
- **Sin spread ni comisiones de v1 a v5; con el spread real en v6.** Si en una misma vela caben stop y objetivo, cuenta el stop (pesimista).
- Sesgo reconstruido con las **reglas actuales del bot**: ruptura del día de trading anterior ×2, precio vs TDO ×1 y precio vs
  Midnight (00:00 NY) ×1; sesgo con |puntuación| ≥ 2. Hasta la v6 inclusive el análisis usaba ruptura ×2 + apertura del día ×1 (la
  columna «sesgo (reglas antiguas)» de los Excel la conserva). Se calcula en la vela del disparo, sin mirar al futuro.
- R = múltiplo del riesgo inicial. Las operaciones aún abiertas al final de los datos no cuentan en las estadísticas.
- El estadístico t del R medio sirve de guía de fiabilidad: |t| > 2 es una diferencia con cierta solidez. Al mirar muchas tablas
  (por TBR, mercado, hora...) algunas «ventajas» salen por azar.

## Resumen

| Versión | Estrategia | Operaciones | Win rate | R medio | Profit factor | Máx. drawdown | Peor racha | t |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| v1 | Orden límite en el nivel roto, stop bajo el mínimo del retest | 10.116 | 36,2 % | **−0,105** | 0,83 | −1.080R | 22 | −8,9 |
| v2 | Entrada a mercado en la 2ª ruptura | 10.992 | 42,1 % | +0,007 | 1,01 | −249R | 22 | 0,6 |
| v3 | v2 + stop en el extremo opuesto de la TBR | 10.998 | 51,2 % | +0,008 | 1,02 | −135R | 10 | 0,8 |
| v4 | v3 + filtro de rango mínimo | 7.345 | 51,8 % | +0,022 | 1,04 | −64R | 14 | 1,8 |
| v5 | v4 con stop en el 50 % y objetivo a 1,5 rangos | 7.299 | 27,4 % | +0,060 | 1,08 | −135R | 37 | 1,7 |
| v6 | **v5 con el spread real** | 7.313 | 26,6 % | **−0,046** | 0,94 | −487R | 37 | **−2,3** |
| v7 | v6 + Bias Execution: solo a favor del sesgo | 4.273 | 29,8 % | **−0,001** | 1,00 | −167R | 25 | −0,03 |
| v8 | v6 sin operar contra el sesgo | 6.443 | 27,6 % | −0,030 | 0,96 | −351R | 33 | −1,4 |
| v9 | v6 con Bias Execution usando solo el barrido de la vela anterior | 1.048 | 24,9 % | −0,082 | 0,89 | −149R | 23 | −1,6 |
| v10 | v7 con el barrido sumado a las reglas actuales (peso 2) | 3.825 | 29,0 % | −0,029 | 0,96 | −218R | 26 | −1,1 |

La reversión C (propuesta, aún no implementada) no cambia entre versiones: 8.057 operaciones, R medio +0,013, PF 1,02,
máx. drawdown −178R.

## v1: línea base

La estrategia tal como está en la skill Setup (commit `4d0d94e`): orden **límite** en el nivel roto, stop bajo el mínimo del
retest (el más bajo entre la toma y la segunda ruptura) y objetivo en el nivel −1 (un rango más allá del nivel roto).

Resultado: **−0,106R por operación** con un t de −8,9. Es una pérdida clara y consistente en las 5 TBR, los 6 mercados y ambas
direcciones. Diagnóstico (ver hojas del Excel): el 92 % de las órdenes se llena en las 2 velas siguientes a la segunda ruptura
(R medio −0,12); las que se llenan 3 o más velas después son ligeramente positivas, pero son solo 860.

## v2: entrada a mercado

**Cambio.** La entrada pasa de orden límite en el nivel roto a **mercado, en la apertura de la vela siguiente a la segunda
ruptura**. Stop y objetivo no cambian.

**Por qué.** La orden límite sufre *selección adversa*: se llena sobre todo en los trades que retestan enseguida (los que fallan
más) y no se llena en los que despegan sin volver. Entrar a mercado elimina ese filtro involuntario.

**Resultado.** R medio de −0,106 a **+0,007** (+0,113R). Es la mejora más grande de todas: la pérdida entera de v1 venía de
la forma de entrar. Las 879 operaciones nuevas (10.993 frente a 10.114) son las que la orden límite nunca llenaba.
Queda en el punto de equilibrio (t = 0,5): sin ventaja estadística.

**Trampa evitada.** Las 1.147 órdenes de v1 que caducan «porque el precio llegó al objetivo sin llenarse» salían con +0,54R a
mercado, pero eso es sesgo de selección (son ganadoras por construcción). La cifra válida es la de v2, que usa *todas* las
segundas rupturas.

## v3: stop en el extremo opuesto de la TBR

**Cambio.** Sobre v2, el stop pasa de bajo el mínimo del retest al **Low de la TBR** (al High en cortos).

**Por qué.** El stop del retest queda a 0,5–0,65 rangos de la entrada y el ruido lo barre; con él más lejos deberían sobrevivir
más operaciones.

**Resultado.** R medio +0,009 (sin cambio real), pero el perfil de riesgo mejora mucho: win rate de 42 % a 51 %, máximo drawdown
de −248R a **−135R** y peor racha perdedora de 22 a 10. Es decir, el mismo R medio con menos sufrimiento. El riesgo medio
pasa a ser ≈ 1,0 rango y el R potencial medio ≈ 1,1.

## v4: filtro de rango mínimo

**Cambio.** Sobre v3, solo se opera si el rango de la TBR es **al menos el 80 % de la mediana de sus últimas 20 sesiones** (la
misma TBR del mismo mercado). Se calcula con datos anteriores, sin mirar al futuro. Deja 7.354 de las 10.995 operaciones.

**Por qué.** En v1–v3 el cuartil de rangos más estrechos es sistemáticamente el peor (en v3: −0,033R con win rate del 49,7 %, el único
tramo negativo). Con rangos pequeños pesan más el ruido y, en la práctica, el spread.

**Resultado.** R medio **+0,022** (t = 1,75), profit factor 1,04, drawdown −64R. Es estable en el tiempo: +0,022 en la primera
mitad del histórico y +0,021 en la segunda. Mejora en las 5 TBR; Pre-NY pasa a +0,097 y NY-PM sigue negativa (−0,021).

## v5: stop en el 50 % y objetivo a 1,5 rangos

**Cambio.** Sobre v4, el stop pasa del extremo opuesto al **50 % de la TBR** y el objetivo de 1 a **1,5 rangos** más allá del
nivel roto (el nivel −1,5 de Fibonacci).

**Por qué y cómo se eligió.** Para no sobreajustar, la combinación se eligió con la **primera mitad** del histórico (hoja
«Sensibilidad 1ª vs 2ª mitad» de v4: stop en el 50 % y objetivo 1,5 era la mejor celda, +0,062R) y se comprobó en la
**segunda mitad** (+0,092R en v4; +0,074R en v5). Lógica de mercado: si el precio vuelve al 50 % tras la segunda ruptura, la
continuación ha fallado, y es el stop natural; con él, un objetivo más lejano compensa los stops más frecuentes.

**Resultado.** R medio **+0,061**, PF 1,08, win rate 27,4 %, profit factor mejor que en cualquier versión. Pero hay avisos claros:

- **Peor racha de 37 pérdidas** y drawdown de −135R: es una estrategia de pocos aciertos y mucha paciencia.
- **El resultado depende de pocos sitios:** DJ30.r (+0,305R) y Pre-NY (+0,283R) concentran la ventaja; EURUSD (−0,058R) y NY-AM
  (−0,049R) son negativos. El resto ronda el cero.
- **No es estable por años:** 2022 +0,175, 2023 +0,074, 2024 −0,018, 2025 +0,144, 2026 −0,020 (2026 incompleto).
- t = 1,73: no llega a 2.
- **Dirección:** largos +0,087R frente a cortos +0,033R.

## v6: v5 con el spread real

**Cambio.** Misma estrategia que v5 (entrada a mercado, stop en el 50 %, objetivo a 1,5 rangos, filtro de rango), pero aplicando
el **spread real que MT5 registra en cada vela** (Vantage demo, `spread` en puntos × tamaño del punto). Mediana: NAS100.r 1,5
puntos, SP500.r 0,6, DJ30.r 3,0, EURUSD y GBPUSD 1,2 pips, XAUUSD 0,18 dólares. Las velas son de precio bid: el largo compra al
ask (entrada + spread) y sale al bid; el corto vende al bid y sale al ask, así que su stop y su objetivo saltan un spread antes
en las velas bid. El riesgo (1R) incluye el spread. Se usa el spread de la vela de entrada para la entrada y la salida (aproximación).
No incluye comisiones (la cuenta demo parece sin comisión; confirmar con el broker).

**Por qué.** Hasta v5 no había costes y la ventaja era de +0,06R: había que saber si el spread se la comía.

**Resultado.** **R medio −0,046**, profit factor 0,94, t = −2,3, drawdown −487R. **Con el spread real la estrategia pierde.** El spread
cuesta **0,10R por operación** (el doble de lo que estimé a ojo: 0,02–0,06R), porque los rangos de las TBR son pequeños frente al
spread: el spread medio es el 8,4 % del riesgo de la operación.

- **Por mercado** (R medio con spread, sin spread): XAUUSD +0,012 (+0,045), DJ30.r +0,052 (+0,308), SP500.r −0,029 (+0,068),
  NAS100.r −0,050 (−0,013), GBPUSD −0,099 (+0,004) y EURUSD −0,159 (−0,059). El spread se come el 80–100 % de la ventaja en
  todos menos en DJ30.r, que aguanta 1,2 veces su spread, y XAUUSD, 1,4.
- **Por TBR:** solo Pre-NY sigue en positivo (+0,077); NY-AM (−0,106) y NY-PM (−0,124) son las peores.
- **Por dirección:** largos +0,010 y cortos −0,106.
- **Sensibilidad (hoja del Excel):** ninguna combinación de stop y objetivo sale positiva con spread; las mejores quedan en
  −0,007R (stop bajo el retest o en el extremo, objetivo 1,5 rangos), y esto se repite en las dos mitades del histórico.
- **Por años:** +0,124 (2022), +0,004 (2023), −0,142 (2024), −0,041 (2025), −0,078 (2026).
- **Por coste relativo:** las operaciones con spread por encima del 8,6 % del riesgo pierden −0,207R; las de coste medio
  (2,5–8,6 %) rondan +0,01 a +0,05R. Sugiere un filtro de coste (ver próximas iteraciones).

## v7 y v8: el Bias como filtro (reglas TDO y Midnight)

**Cambio.** Se reconstruye el sesgo con las reglas actuales del bot y se usa como filtro de Bias Execution sobre v6:

- **v7:** solo operaciones **a favor del sesgo** (lo que hace el bot con `BIAS_EXEC_ALLOW_NO_BIAS=false`).
- **v8:** se descartan solo las operaciones **contra el sesgo** (a favor o sin sesgo; equivale a `ALLOW_NO_BIAS=true`).

**Por qué.** Las reglas TDO y Midnight se añadieron al Bias sin medirlas. Esto las mide como filtro y regla por regla.

**Resultado (continuación, con spread real):**

| Filtro | Operaciones | R medio | Profit factor | Máx. drawdown | t |
|---|---:|---:|---:|---:|---:|
| Sin filtro (v6) | 7.313 | −0,046 | 0,94 | −487R | −2,3 |
| **Solo a favor del sesgo (v7)** | 4.273 | **−0,001** | 1,00 | −167R | −0,03 |
| A favor o sin sesgo (v8) | 6.443 | −0,030 | 0,96 | −351R | −1,4 |
| Solo contra el sesgo | 870 | **−0,169** | 0,79 | −170R | −2,6 |
| Solo sin sesgo | 2.170 | −0,087 | 0,89 | −217R | −2,2 |

- **El Bias sí aporta como filtro:** deja la continuación en el punto de equilibrio (de −0,046R a −0,001R) y recorta el drawdown a
  un tercio. Casi todo el beneficio viene de evitar las operaciones contra el sesgo y las que no tienen sesgo.
- **Pero no hace rentable la continuación:** el mejor resultado es cero, no positivo.
- **Las reglas nuevas filtran mejor que las antiguas** en volumen: con ellas el 58 % de las operaciones tienen sesgo a favor, frente
  al 20 % con la apertura del día (4.273 frente a 1.439), y con el mismo R medio (−0,001 frente a −0,012).

**Aportación de cada regla** (hoja «Aportación por regla»; R medio de la continuación según el voto de la regla frente a la operación):

| Regla | Apoya la operación | Neutra | Contra la operación |
|---|---:|---:|---:|
| Ruptura del día anterior | −0,018 (n=1.469) | −0,053 | −0,073 (n=209) |
| **TDO** | −0,025 (n=5.537) | — | **−0,114** (n=1.771, t −2,5) |
| **Midnight** | −0,017 (n=4.837) | −0,028 | **−0,154** (n=1.464, t −3,1) |

El **Midnight es la regla más informativa**: con la operación contra el Midnight la continuación pierde −0,154R; el TDO le sigue.
La ruptura del día anterior discrimina menos, aunque apenas da casos (el precio rara vez está fuera del rango previo).

## v9 y v10: regla de barrido de la vela anterior (H3 en índices, H4 en el resto)

**Criterio** (definido por ti). El sesgo de la vela actual (la 0) se calcula con las dos anteriores ya cerradas, la n‑1 y la
n‑2. Si la n‑1 **barre el High de la n‑2 y cierra dentro de su rango**, el sesgo es **bajista**; si **barre el Low y cierra dentro**,
**alcista**. Si barre los dos lados, cierra fuera (ruptura) o no barre ninguno, no hay sesgo y la regla no puntúa. Las velas se
alinean con el inicio del día de trading en NY (H3: 18, 21, 00, 03...; H4: 17, 21, 01, 05...). Está implementada como regla
`htf_sweep` (peso 2 por defecto, **no activa por defecto**) y se reconstruye en el análisis con los mismos datos.

**Cambio.**
- **v9:** sobre v6, solo se opera a favor del sesgo que da el barrido (sin barrido válido no hay sesgo y no se opera).
- **v10:** sobre v7, el barrido (peso 2) se suma a las reglas actuales (ruptura ×2, TDO, Midnight); solo a favor del sesgo.

**Por qué.** Medir si el primer criterio nuevo de Bias aporta, aislado y combinado.

**Resultado como filtro de los setups** (con spread real):

| Filtro | Operaciones | R medio | Máx. drawdown |
|---|---:|---:|---:|
| Sin filtro (v6) | 7.312 | −0,046 | −487R |
| Reglas actuales a favor (v7) | 4.273 | −0,001 | −167R |
| **Solo barrido a favor (v9)** | 1.048 | **−0,082** | −149R |
| **Reglas actuales + barrido a favor (v10)** | 3.825 | **−0,029** | −218R |

- **El barrido empeora los resultados.** Solo, queda por debajo de no filtrar; sumado a las reglas actuales, pasa de −0,001R a −0,029R.
- Aportación de la regla a la continuación: cuando el barrido **apoya** la operación −0,082R (n = 1.048), si es **neutro** −0,056R
  (n = 4.514) y si va **en contra** +0,001R (n = 1.750). Es decir, el efecto es al revés de lo esperado, aunque sin significación
  (t de −1,6 y 0,0).
- En la reversión C, el barrido a favor da −0,056R (n = 1.832) y sumado a las reglas actuales, −0,016R (antes +0,007R).

**Medida directa: ¿la vela 0 cierra en la dirección del sesgo?** (hoja «Barrido - predicción vela», independiente de los setups).
Los mercados subieron en este periodo, así que hay que restar lo que haría cualquier vela (el 52,5 % cierra al alza sin ninguna
regla). El 71 % de las velas no tiene sesgo, el 14,6 % es bajista y el 14,2 % alcista.

| Sesgo del barrido | Velas | Acierta la dirección | Una vela cualquiera | Ventaja de acierto | Ventaja de movimiento | t |
|---|---:|---:|---:|---:|---:|---:|
| Bajista (barrió el High) | 6.616 | 48,4 % | 47,5 % | +0,9 puntos | −0,004 rangos | −0,3 |
| Alcista (barrió el Low) | 6.412 | 52,8 % | 52,5 % | +0,3 puntos | +0,027 rangos | 2,1 |

- **El barrido no anticipa la dirección de la vela:** acierta lo mismo que el azar (la ventaja es de menos de un punto).
- **Lado bajista:** ninguna ventaja (t = −0,3).
- **Lado alcista:** una ventaja mínima, del 2,7 % del rango de la vela anterior (t = 2,1), que con tantas pruebas puede ser azar.
- Por mercados no hay un patrón: XAUUSD y DJ30.r salen algo mejor en el lado alcista, NAS100.r y SP500.r salen sin ventaja.

**Conclusión.** Con la definición actual (barrer el High o el Low de la n‑2 y cerrar dentro), el barrido **no aporta información
útil** sobre la dirección de la vela ni mejora los setups de las TBR en estos mercados. Se deja implementado pero inactivo.

**Ideas para una segunda regla** (a definir contigo): probar la lectura contraria (barrer y cerrar fuera como *continuación*),
medir el barrido de la vela n‑1 con la dirección del día (TDO / Midnight) como filtro, o usar otros marcos temporales (H1 o H12).

## v11 y v12: regla de continuación de la vela anterior, y sesgo congelado por vela HTF

**Cambio de metodología (afecta a v7-v12).** El sesgo total solo se recalcula al crearse la vela 0 (H3 en índices, H4 en el
resto) y se mantiene hasta la siguiente. Se calcula con el precio de apertura de esa vela, sin mirar al futuro. Antes, la
ruptura del día anterior, el TDO y el Midnight se evaluaban en cada vela de M15. El bot en vivo hace lo mismo: los niveles solo
recalculan el sesgo si falta el TDO o es de otro día.

**Regla de continuación (`htf_break`).** Si la vela n-1 cierra sobre el High de la n-2, el voto es +1; si cierra bajo el Low,
-1. Si cierra dentro, la n-1 es interna o barre con mecha el High y el Low de la n-2 (envolvente), el voto es 0.

| versión | operaciones | win rate % | R medio | R total | profit factor | max drawdown (R) |
|---|---|---|---|---|---|---|
| v7 (reglas actuales, a favor) | 2925 | 28,3 | 0,000 | +1,3 | 1,00 | -155,6 |
| v11 (solo continuación) | 1543 | 26,8 | -0,024 | -36,9 | 0,97 | -81,2 |
| v12 (reglas actuales + continuación, peso 2) | 3216 | 27,6 | -0,014 | -45,6 | 0,98 | -184,4 |

**Predicción directa de la vela 0** (hojas «Barrido - predicción vela» y «Continuación - predicción vela»): ninguna de las dos
reglas supera al azar de forma útil.
- Barrido: bajista 48,5 % de acierto frente a 47,5 % de una vela cualquiera (+0,9 puntos); alcista 52,8 % frente a 52,5 % (+0,3).
- Continuación: bajista 47,2 % frente a 47,5 % (-0,3 puntos); alcista 51,8 % frente a 52,5 % (-0,7).

**Lectura.** Congelar el sesgo por vela no cambia el resultado de v7 (R medio 0,000, antes -0,001). La continuación de la vela
anterior no aporta información direccional y no mejora la estrategia: v12 queda por debajo de v7. Ni el barrido ni la
continuación justifican, de momento, activarse por defecto.

## Reversión C con spread real (cambio de metodología)

**Cambio.** Hasta ahora la reversión C se simulaba **sin costes** (v1–v5) y en la versión anterior de este documento se le restó
el spread de forma aproximada. Desde esta iteración, en v6–v8 se simula **en precios reales con el spread de cada vela**: la venta
límite se llena con el bid y la compra límite con el ask; el stop y el objetivo se activan por el lado que corresponde (en un corto,
por el ask) y el riesgo (1R) incluye el spread. La orden caduca si antes de llenarse el precio llega al objetivo o pasa la
ventana de 24 h. La comparación de ambas simulaciones está en la hoja «Comparativa reversión C».

**Por qué.** La aproximación (R − spread/riesgo) no capta que el spread cambia qué órdenes se llenan y cuándo saltan stop y
objetivo. Había que comprobar si el +0,058R de la reversión a favor del sesgo sobrevivía a los costes.

**Resultado** (reglas actuales del sesgo):

| Filtro | Operaciones | R medio sin costes (v5) | **R medio con spread real (v6)** | Profit factor | Máx. drawdown | t |
|---|---:|---:|---:|---:|---:|---:|
| Sin filtro | 7.979 | +0,015 | **−0,033** | 0,95 | −338R | −1,9 |
| **Solo a favor del sesgo** | 4.062 | **+0,058** | **+0,007** | 1,01 | −107R | 0,3 |
| A favor o sin sesgo | 6.833 | +0,023 | −0,024 | 0,97 | −284R | −1,3 |

- **Con el spread real, la reversión a favor del sesgo queda en el punto de equilibrio** (+0,007R, t = 0,3): la ventaja de +0,058R
  desaparece. La aproximación anterior (+0,009R) era buena.
- **No es estable en el tiempo:** +0,038R en la primera mitad del histórico y −0,025R en la segunda; por años, de −0,038 (2022) a
  +0,069 (2023), −0,024 (2025) y −0,008 (2026).
- **Por mercado (a favor del sesgo, con spread):** XAUUSD +0,117, NAS100.r +0,042, SP500.r +0,034, DJ30.r +0,028; EURUSD −0,109 y
  GBPUSD −0,093. Es el mismo patrón que en la continuación: los mercados cuyo spread pesa menos frente al rango aguantan, los
  del forex no.
- **Por TBR:** Asia +0,029, NY-PM +0,018, NY-AM +0,014; London −0,018 y Pre-NY −0,019.
- **Por dirección:** largos +0,022 y cortos −0,012.
- El spread medio de la reversión es 0,056R de su riesgo. Es menor que en la continuación (0,084R) porque el stop de la reversión
  (el High tomado) está más lejos.
- **Una pista a verificar:** las operaciones con spread medio (entre el 2 % y el 6 % del riesgo) rinden +0,07 a +0,09R (n ≈ 2.030),
  mientras que las de spread muy pequeño (rangos muy grandes) y las de spread alto (rangos pequeños) pierden −0,06 a −0,08R. Es un
  cruce entre muchos y no se debe usar como regla sin confirmarlo con datos nuevos.

## Qué dicen los datos hasta ahora

1. La causa principal de la pérdida de v1 era **la orden límite** (selección adversa), no la idea de las TBR.
2. Con entrada a mercado el patrón es **neutro antes de costes**: ni gana ni pierde. Lo que mejoran v3–v5 es el perfil de riesgo
   (drawdown, rachas) y, ligeramente, el R medio.
3. Filtrar rangos pequeños es lo que más ayuda de forma estable (v4), y el spread explica por qué: los rangos pequeños son donde
   más pesa.
4. **Con el spread real (v6), la mejor versión de la continuación pierde 0,046R por operación.** La ventaja bruta de v5 (+0,06R)
   es menor que el coste (0,10R).
5. **El Bias con TDO y Midnight sí aporta como filtro:** sube la continuación de −0,046R a −0,001R y recorta el drawdown a un
   tercio. El **Midnight** es la regla más informativa, seguido del TDO. Pero el mejor resultado es el equilibrio: el Bias evita
   perder, no crea ventaja por sí solo.
6. **La reversión C a favor del sesgo era lo más prometedor** (+0,058R sin costes, t = 2,4), pero con el spread real queda en
   **+0,007R** (t = 0,3): equilibrio, y con una mitad del histórico positiva y la otra negativa.
7. Solo sobreviven bolsillos pequeños (DJ30.r, XAUUSD, NAS100.r, Pre-NY, largos), y mantenerlos sin datos fuera de muestra sería
   sobreajuste.

## Próximas iteraciones propuestas

- **v7: filtro de coste.** Operar solo si el spread es menor que cierto porcentaje del riesgo (p. ej. 8 %): descarta los rangos
  pequeños donde el spread domina. Se mide con el spread de cada vela, sin mirar al futuro. Hay que confirmarlo en las dos mitades.
- **Rangos más grandes o más tiempo:** probar TBR agrupadas o velas de mayor tamaño (M30/H1) para que el spread pese menos.
- Aplicar a la **reversión C** las mejoras de la continuación (filtro de rango y de coste) ahora que se simula con spread real.
- **Más reglas para el Bias**, probadas una a una como se ha hecho con TDO y Midnight (p. ej. dónde cerró la sesión asiática o
  londinense respecto a su TBR, o la dirección de la última TBR cerrada). El Midnight ha sido la más informativa: otras reglas de
  tiempo y apertura podrían serlo también.
- Probar la **reversión C a favor del sesgo con un filtro de coste** (v7 propuesta) y con velas mayores, para que el spread pese menos.
- Confirmar las **comisiones** de la cuenta real antes de decidir nada.
