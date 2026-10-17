# ¿Hay algún subconjunto de operaciones con ventaja real?

Scripts: `scripts/buscar_subconjuntos.py` (sobre `analisis/backtest_patrones.xlsx`) y `scripts/deriva_semanal.py`.

## Método

Las 10.384 operaciones del backtest de Continuación y Reversión (2018-2026) se agrupan por todo lo que se sabe antes de entrar: mercado,
patrón, zona, dirección, franja horaria, día de la semana, año, sesgo (a favor, en contra o sin él), lateral, puntuación del sesgo, tamaño
del riesgo y coste (spread / riesgo). Se probaron **4.373 combinaciones** de una, dos y tres características (con al menos 120 operaciones),
se eligió con el 60 % más antiguo y se validó con el 40 % final. Para saber cuánto sale bueno solo por probar tantas, se repitió todo 300
veces con los resultados barajados entre las operaciones. Se hizo con el R neto y con el R bruto (sin costes), porque los costes varían
mucho entre mercados.

## Resultado

**Los patrones en general no tienen ventaja, pero hay un efecto que se repite: los largos de los lunes.**

- **El mejor subconjunto del entrenamiento** (Reversión, 06-09 NY, riesgo muy alto) ganó +0,53 R y en validación +0,10 R (t = 0,5): no se
  confirma.
- **Mejor t sobre todo el histórico:** 3,61 (R neto) y 4,31 (R bruto), frente a 2,9 y 3,9 que alcanza el azar en el 5 % de las veces.
  Los subconjuntos positivos en las dos mitades superan lo esperable por azar (383 frente a 156 con R neto; 1.185 frente a 1.079 con bruto).
- **Los costes** explican gran parte de las diferencias entre mercados: el NAS100 es el de menor coste relativo y el US2000 el de mayor.

## Largos en lunes (ventana Asia + London)

| Largos en lunes | Operaciones | R bruto | R neto | t (neto) |
|---|---:|---:|---:|---:|
| Todas las zonas | 1.046 | +0,19 | +0,09 | 1,9 |
| London | 709 | +0,23 | +0,15 | 2,7 |
| A favor del sesgo | 444 | +0,28 | +0,19 | 2,7 |
| NAS100 | 302 | +0,37 | +0,31 | 3,6 |
| Resto de largos (no lunes) | 4.224 | +0,01 | -0,09 | -4,1 |
| Cortos en lunes | 917 | -0,09 | -0,20 | -4,4 |

- **Se replica fuera de la muestra.** El efecto se vio primero con las velas de 2022-2026. Con las velas añadidas de 2018 a julio de 2022
  (que no se habían usado), los largos de lunes dan **+0,189 R bruto** (+0,114 neto, 421 operaciones) y los de London +0,207 bruto (314
  operaciones); los cortos de lunes pierden igual (-0,16 neto). Son casi las mismas cifras que en la muestra donde se halló.
- Positivo en las dos mitades (+0,17 / +0,21 bruto), en 8 de los 9 años y en 3 de los 4 mercados (US2000 es negativo).
- **Contraste independiente** (`scripts/deriva_semanal.py`, velas H1, 10-18 años): la ventana de las 20:00 a las 10:00 NY **de los
  lunes** sube de media +0,08 % a +0,125 % en los cuatro índices (t = 2,4-2,5 en cada uno); martes, jueves y viernes son ≈ 0. Es la
  deriva alcista nocturna conocida de los índices: los largos de lunes de los patrones la están capturando.
- Otra pista más débil: Reversión con riesgo muy alto (+0,29 R neto, 225 operaciones; validación +0,20 R, t = 1,1).

## Cómo leerlo

- La ventaja, si existe, está en **cuándo** se entra (lunes, largo, sesión asiática y de Londres), no en los patrones: una entrada larga
  cualquiera en esa ventana captura el mismo efecto.
- Neto de costes son +0,09 R (todas las zonas) a +0,19 R (a favor del sesgo) por operación, con unas 55 a 130 operaciones al año entre los
  cuatro mercados: del orden de 10-13 R al año. Es una ventaja pequeña, y se ha mirado entre miles de combinaciones.
- Siguiente paso razonable: medirlo como una sola hipótesis (largos de lunes en la ventana Asia + London), con entrada a hora fija y
  sin patrones, y compararlo con las entradas de los patrones; y seguirlo en demo antes de darlo por bueno.
