# Análisis histórico de los setups: cambios entre versiones

Registro de cada iteración de la estrategia de continuación sobre las TBR. Cada versión se calcula con **los mismos datos** y
tiene su Excel (`analisis/analisis_setups_vN.xlsx`, generado por `scripts/analisis_setups.py`; la carpeta `analisis/` no se sube
a git). Cada Excel incluye las hojas **Cambios** (qué cambia y por qué) y **Comparativa** (todas las versiones, por TBR y por sesgo).

## Datos y método (iguales en todas las versiones)

- Velas M15 de MT5 (Vantage demo), ~100.000 por mercado (≈ oct 2022 – oct 2026): NAS100.r, SP500.r, DJ30.r, EURUSD, GBPUSD, XAUUSD.
- Hora de Nueva York (servidor = NY + 7 h). Día de trading desde las 18:00 NY en índices USA y 17:00 en el resto.
- Setup: toma de liquidez del High/Low de la TBR, retest del 50 % y segunda ruptura (la skill Setup, `detect`). Se invalida si toma
  el lado contrario; ventana de 24 h para completar el setup y 48 h para resolver la operación.
- **Sin spread ni comisiones.** Si en una misma vela caben stop y objetivo, cuenta el stop (pesimista).
- Sesgo reconstruido con las dos reglas del bot (ruptura del día previo ×2, precio vs apertura ×1; sesgo con |puntuación| ≥ 2).
  Es una aproximación: el 80 % de las operaciones salen «sin sesgo».
- R = múltiplo del riesgo inicial. Las operaciones aún abiertas al final de los datos no cuentan en las estadísticas.
- El estadístico t del R medio sirve de guía de fiabilidad: |t| > 2 es una diferencia con cierta solidez. Al mirar muchas tablas
  (por TBR, mercado, hora...) algunas «ventajas» salen por azar.

## Resumen

| Versión | Estrategia | Operaciones | Win rate | R medio | Profit factor | Máx. drawdown | Peor racha | t |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| v1 | Orden límite en el nivel roto, stop bajo el mínimo del retest | 10.114 | 36,2 % | **−0,106** | 0,83 | −1.092R | 22 | −8,9 |
| v2 | Entrada a mercado en la 2ª ruptura | 10.993 | 42,1 % | +0,007 | 1,01 | −248R | 22 | 0,5 |
| v3 | v2 + stop en el extremo opuesto de la TBR | 10.995 | 51,3 % | +0,009 | 1,02 | −135R | 10 | 0,9 |
| v4 | v3 + filtro de rango mínimo | 7.354 | 51,8 % | +0,022 | 1,04 | −64R | 14 | 1,75 |
| v5 | v4 con stop en el 50 % y objetivo a 1,5 rangos | 7.308 | 27,4 % | **+0,061** | 1,08 | −135R | 37 | 1,73 |

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

## Qué dicen los datos hasta ahora

1. La causa principal de la pérdida de v1 era **la orden límite** (selección adversa), no la idea de las TBR.
2. Con entrada a mercado el patrón es **neutro**: ni gana ni pierde antes de costes. Lo que mejoran v3–v5 es el perfil de riesgo
   (drawdown, rachas) y, ligeramente, el R medio.
3. Filtrar rangos pequeños es lo que más ayuda de forma estable (v4).
4. v5 es la mejor versión hasta ahora, pero su ventaja es fina (+0,061R) y frágil. Para comparar: un spread típico supone, a
   ojo y sin medir, del orden de 0,02 a 0,06R por operación en estos mercados (el riesgo medio es el 0,13 % del precio en EURUSD
   y GBPUSD y el 0,24–0,36 % en índices y oro). **Con costes reales v5 podría quedar en el punto de equilibrio.**

## Próximas iteraciones propuestas

- **v6: spread y comisión reales** por mercado (sin ellos no se puede decidir si hay ventaja de verdad).
- Mejor reconstrucción del **Bias** (más reglas): hoy el 80 % de las operaciones salen sin sesgo y los resultados «a favor» y
  «contra» no son concluyentes.
- Evaluar por separado la **reversión C** con entrada a mercado y las mismas mejoras (filtro de rango, stop).
- Aplicar a v5 los filtros por **TBR y mercado** solo si se confirman en datos nuevos (mantener Pre-NY, DJ30 y los largos sin
  datos fuera de muestra sería sobreajuste).
