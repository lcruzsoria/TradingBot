# Backtest del sesgo en M5: reglas, pesos, umbral y filtro de lateralidad

Script: `scripts/analisis_sesgo.py --perfil <perfil>` (datos: `scripts/descargar_m5.py --perfil <perfil>`). Solo lee velas; el bot no envía órdenes.
Actualizado el 21/10/2026, con el sweep mecha ya con el criterio de la envolvente (ver `bias/htf.py`). El perfil Calendario no usa sesgo y no se mide.

## Cómo se midió

- **Un backtest por perfil**, porque cada broker llama distinto a sus símbolos y tiene su propio histórico (hay ~200.000 velas M5 por mercado,
  de octubre-diciembre de 2023 a octubre de 2026):
  - **MetaQuotes:** USTEC, US500, US30, EURUSD, GBPUSD, XAUUSD. 30.308 bloques HTF.
  - **PUPrime:** NAS100.s, SP500.s, DJ30.s, EURUSD, GBPUSD, XAUUSD.s. 30.074 bloques HTF.
  - Bloques de 3 h en índices, de 4 h en el resto.
- **Qué se evalúa:** el sesgo se calcula al abrirse cada bloque (con el precio de apertura, sin mirar al futuro) y se mantiene
  hasta el siguiente, como el bot en vivo. La **ventaja** es lo que hizo el precio en el bloque (cierre menos apertura) en la
  dirección del sesgo, en rangos medios de bloque (los 30 anteriores). Con No Bias no se cuenta.
- **Dos problemas medidos aparte:**
  - *Contradicción:* % de bloques con sesgo contrario a lo que hizo el precio en las 6 h anteriores (un alcista que prohíbe
    cortos con el precio bajista).
  - *Lateral:* % de bloques con sesgo cuando el precio venía lateral (eficiencia de las últimas 6 h < 0,15).
- **Búsqueda:** 1.889.472 combinaciones por perfil: pesos 0/1/2 de nueve reglas candidatas (ruptura del día anterior, TDO, Midnight,
  barrido, continuación, SMA 30, SMA 200, momentum 6 h, momentum 24 h) x umbral 1-6 x filtro de lateralidad (ventanas 3/6/12 h,
  eficiencia mínima 0,10-0,30). Se **optimizó con el primer 60 %** del histórico (18.181 bloques en MetaQuotes, 18.041 en PUPrime) y se
  **validó con el 40 % final**.

## Lo que dicen los datos

1. **Ninguna combinación tiene ventaja estadísticamente significativa y estable** en ninguno de los dos perfiles. La mejor en
   entrenamiento llega a t = +2,81 en MetaQuotes y +3,58 en PUPrime (con 1,9 millones de pruebas, algo así sale por azar), y en
   validación las 25 mejores bajan a t entre -1,8 y -0,6 en MetaQuotes y entre -0,8 y -0,2 en PUPrime. El sesgo, tal como lo definimos, **no es un predictor**: sirve para
   ordenar y filtrar, no para ganar dinero por sí solo.
2. **Las reglas por separado** (peso 1, umbral 1; ventaja en entrenamiento / validación; entre paréntesis, el estadístico t de la
   validación):

| Regla | MetaQuotes entren. / valid. | PUPrime entren. / valid. | Contradice al precio | Lectura |
|---|---:|---:|---:|---|
| `prev_day_break` | +0,104 / -0,036 (t -2,5) | +0,009 / -0,027 (t -1,9) | 11-13 % | pierde en validación en los dos |
| `tdo` | -0,021 / -0,004 | +0,008 / -0,006 | 22 % | sin ventaja |
| `midnight` | -0,009 / -0,004 | +0,019 / -0,001 | 16-17 % | sin ventaja |
| `htf_sweep` | +0,006 / -0,007 | +0,013 / -0,011 | **57-59 %** | reversión: contradice al precio 6 de cada 10 veces |
| `htf_break` | -0,002 / +0,006 | +0,009 / +0,005 | **1 %** | continuación: nunca contradice al precio |
| `sma30` | -0,038 / -0,021 (t -3,2) | -0,003 / -0,017 (t -2,5) | 32-33 % | pierde en validación |
| `sma200` | +0,028 / -0,013 | -0,000 / -0,011 | 19 % | sin ventaja |
| `mom6h` | -0,008 / -0,018 (t -2,6) | -0,003 / -0,014 (t -2,1) | 1 % | pierde en validación |
| `mom24h` | +0,028 / -0,019 (t -2,8) | -0,005 / -0,016 (t -2,3) | 35 % | pierde en validación |

   Sobre el criterio nuevo del sweep (la envolvente que cierra fuera puntúa): bajó las contradicciones del 76 % al 57-59 %, pero la ventaja
   sigue en torno a cero (t de validación -0,66 en MetaQuotes y -1,0 en PUPrime). Sigue siendo una regla de reversión que no suma.

3. **El filtro de lateralidad es lo que más mejora el comportamiento visible.** Sin él, el 57-61 % de los bloques tiene sesgo y el
   **57-58 % de esos arranca con el mercado lateral**. Con el filtro (eficiencia de 6 h ≥ 0,15) quedan sesgos solo en el 26-27 % de los
   bloques y ninguno en lateral.
4. **El sesgo que contradice al precio viene sobre todo de `htf_sweep`** (reversión) y, en menor medida, de `tdo`/`sma30`/`mom24h`.

## Combinaciones comparadas (todas con los mismos datos de cada perfil)

Ventaja total en rangos de bloque (estadístico t entre paréntesis). A y B son las del backtest anterior; B ya usa el sweep con el criterio nuevo.

| Config. | Reglas / pesos | Umbral | Filtro | Cobertura | MetaQuotes: entren. / valid. / total (t) | PUPrime: entren. / valid. / total (t) | Contradice | Lateral |
|---|---|---:|---|---:|---|---|---:|---:|
| A (por defecto antiguo) | ruptura 2, TDO 1, Midnight 1 | 2 | no | 57 % | +0,007 / -0,008 / +0,001 (t +0,1) | +0,012 / -0,007 / +0,004 (t +0,7) | 11-12 % | 57-59 % |
| B (local antiguo) | ruptura 2, TDO 2, Midnight 1, barrido 2, continuación 2 | 3 | no | 60 % | +0,013 / -0,003 / +0,007 (t +1,0) | +0,009 / -0,005 / +0,003 (t +0,6) | 13,5 % | 56-57 % |
| D (sin filtro) | ruptura 2, TDO 2, Midnight 1, continuación 2 | 3 | no | 61 % | +0,016 / -0,003 / +0,008 (t +1,2) | +0,010 / -0,003 / +0,005 (t +0,8) | 9,5-10 % | 56-57 % |
| **C (aplicada)** | **ruptura 2, TDO 2, Midnight 1, continuación 2** | **3** | **eficiencia 6 h ≥ 0,15** | **26-27 %** | **+0,015 / -0,000 / +0,009 (t +0,9)** | **+0,012 / +0,013 / +0,012 (t +1,3)** | **0,6-1,4 %** | **0 %** |

Por mercado (estadístico t de la ventaja total de C):
- **MetaQuotes:** US500 +0,88, XAUUSD +0,82, USTEC +0,76, US30 +0,23, GBPUSD -0,13, EURUSD -0,87.
- **PUPrime:** NAS100.s +1,25, SP500.s +0,99, DJ30.s +0,82, XAUUSD.s +0,64, GBPUSD +0,18, EURUSD -1,13.

En los dos perfiles los índices y el oro salen positivos y el EURUSD negativo, pero ninguno es significativo por separado.

## Decisión aplicada

Sin cambios respecto al backtest anterior: la nueva medición no ofrece ninguna combinación mejor en validación, así que `BIAS_RULES` se mantiene.

- **Reglas:** `prev_day_break` (2), `tdo` (2), `midnight` (1), `htf_break` (2). `htf_sweep` sigue fuera (contradice al precio 57-59 % de las
  veces) y `above_below_open` también (duplica al TDO). `sma` queda disponible pero **apagada**: la SMA 30 pierde en validación.
- **Umbral 3:** una regla de peso 2 ya no basta sola; hacen falta dos que coincidan.
- **Filtro de lateralidad** (`BIAS_LATERAL_HOURS=6`, `BIAS_LATERAL_MIN_EFFICIENCY=0.15`): sin sesgo si el precio avanzó menos del
  15 % de su recorrido en las últimas 6 h. Ajustable en la ventana de reglas.

## Limitaciones (importante)

- Con tantas combinaciones probadas, que C sea la «mejor» sale en parte del azar: su ventaja total (+0,009 y +0,012 rangos de bloque, t 0,9 y 1,3)
  **no es significativa**. Lo que sí se mantiene, en los dos perfiles, es el efecto del filtro: menos sesgos, ninguno en lateral y casi
  ninguno contra el precio. C es la única de las cuatro que no pierde en validación en PUPrime y queda en cero (-0,000) en MetaQuotes.
- Las dos mitades del histórico se comportan distinto: casi todo lo que gana en entrenamiento no se repite en validación. 34 meses son pocos
  para fiarse de pesos finos. Conviene repetir el backtest cada pocos meses.
- Los dos perfiles tienen los mismos mercados con distinto broker; que salgan resultados parecidos refuerza la conclusión, pero no son datos
  independientes (mismos precios, hasta el spread y la hora del servidor).
- Se mide la dirección del bloque completo desde su apertura, no la utilidad del sesgo como filtro de los setups de las TBR; para eso
  ver `docs/analisis_setups/CAMBIOS.md` (donde el filtro de sesgo tampoco convirtió en rentable la continuación).
