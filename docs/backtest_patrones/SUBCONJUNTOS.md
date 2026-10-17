# ¿Hay algún subconjunto de operaciones con ventaja real?

Scripts: `scripts/buscar_subconjuntos.py` (sobre `analisis/backtest_patrones.xlsx`) y `scripts/deriva_semanal.py`.

## Método

Las 6.063 operaciones del backtest de Continuación y Reversión se agrupan por todo lo que se sabe antes de entrar: mercado, patrón, zona,
dirección, franja horaria, día de la semana, año, sesgo (a favor, en contra o sin él), lateral, puntuación del sesgo, tamaño del riesgo y
coste (spread / riesgo). Se probaron **3.103 combinaciones** de una, dos y tres características (con al menos 120 operaciones), se
eligió con el primer 60 % del tiempo y se validó con el 40 % final. Para saber cuánto sale bueno solo por probar tantas, se repitió
todo 300 veces con los resultados barajados entre las operaciones (sin ventaja posible). Se hizo con el R neto y con el R bruto (sin
costes), porque los costes varían mucho entre mercados y distorsionan la comparación.

## Resultado

**No hay ningún subconjunto con ventaja confirmada.**

- El mejor subconjunto elegido con el entrenamiento (SP500, largos, lunes) tuvo +0,44 R en entrenamiento y **-0,27 R en validación**.
  En el azar, el mejor de entrenamiento rinde de media -0,13 R en validación: no hay nada que valide.
- Hay 600 subconjuntos positivos en las dos mitades (R bruto), pero el azar ya da 523 de media: no hay exceso.
- El mejor t sobre todo el histórico (R bruto) es 3,49; el azar da un máximo de 2,9 (mediana) y 3,55 (percentil 95): **p = 0,07**, no es
  significativo.
- **Los costes** explican gran parte de las diferencias: R neto por coste de la operación: < 0,05 R: -0,056; 0,05-0,1 R: -0,016;
  0,1-0,2 R: -0,186; > 0,2 R: -0,496. Aun quedándose solo con las operaciones baratas, el resultado es ≈ 0, no positivo.
- El sesgo y la lateralidad no separan buenas de malas operaciones; la puntuación del sesgo ≥ 5 es la menos mala (-0,07 R).

## La única pista: largos en lunes (ventana Asia + London)

| Largos en lunes | Operaciones | R bruto | R neto | t (neto) |
|---|---:|---:|---:|---:|
| Todas las zonas | 625 | +0,19 | +0,07 | 1,2 |
| London | 395 | +0,26 | +0,16 | 2,1 |
| Resto de largos (no lunes) | 2.427 | -0,01 | -0,13 | -4,4 |
| Cortos en lunes | 557 | -0,11 | -0,23 | -4,0 |

- Positivo en las dos mitades (+0,18 / +0,20 bruto), en los 5 años (de +0,05 a +0,25 bruto) y en 3 de los 4 mercados (US2000 es
  negativo). Los cortos en lunes pierden el doble: es un efecto direccional, no de un patrón.
- **Contraste independiente** (`scripts/deriva_semanal.py`, velas H1, 10-18 años): la ventana de las 20:00 a las 10:00 NY **de los
  lunes** sube de media +0,08 % a +0,125 % en los cuatro índices (t = 2,4-2,5 en cada uno), y algo menos los miércoles; martes, jueves y
  viernes son ≈ 0. Es la deriva alcista nocturna conocida de los índices: los largos de lunes de los patrones la están capturando.

## Cómo leerlo

- La ventaja, si existe, está en **cuándo** se entra (lunes, largo, sesión asiática y de Londres), no en los patrones: una entrada
  larga cualquiera en esa ventana captura el mismo efecto.
- Neto de costes sale +0,07 R (todas las zonas) a +0,16 R (London) por operación, con unas 100-150 operaciones al año en los cuatro
  mercados: poco, y ninguna de las dos cifras es estadísticamente sólida al corregir por el número de combinaciones probadas.
- Para confirmarlo hacen falta más datos fuera de muestra (subir «Máx. barras en el gráfico» en MT5 para tener más historia M15, o
  seguirlo unos meses en demo) y definirlo ANTES de mirar, como una sola hipótesis.
