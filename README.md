# TradingBot

Bot de trading con interfaz gráfica sobre MetaTrader 5. Esta primera versión incluye dos tareas y **no opera**:
no existe ninguna llamada para enviar órdenes, solo lectura de datos.

La interfaz sigue el estilo de la referencia visual: azul pizarra oscuro, paneles planos con borde fino,
tarjetas de mercado, gráfico de velas verde azulado/coral y, a la derecha, el sesgo del día.

| Tarea | Qué hace |
|---|---|
| Conexión y velas | Conecta con MT5 usando la cuenta del `.env` y carga todas las velas posibles en 1m, 3m, 5m o 15m (por defecto 15m). |
| Bias | Evalúa las reglas y decide el sesgo del día: **Bullish**, **Bearish** o **No Bias**. Se muestra en un recuadro fijo de la interfaz. |

Cabecera: estado de la conexión, cuenta, saldo/equity, P&L abierto, mercados con precio en vivo y hora del último tick
**en hora de Nueva York**. MT5 entrega los ticks en la hora del servidor de tu broker; el bot mide el desfase de ese
servidor comparando los ticks en vivo con el reloj de tu PC (unos segundos tras conectar) y convierte a Nueva York
respetando el cambio de horario de EE. UU. Hasta que lo mide, la hora se marca como *(estimada)* y asume servidor = Nueva York + 7 h.
Pasa el ratón sobre la caja para ver la hora del servidor y el desfase detectado. Si no lo detecta bien (PC desincronizado),
fíjalo a mano con `server_utc_offset_hours` en `config.toml`. Las horas del eje del gráfico siguen siendo las del servidor.

Panel **Mercados**: cotizaciones de solo lectura (se refrescan cada segundo). Con el botón **Editar** del panel eliges
qué mercados se muestran: busca entre los símbolos reales de tu broker (también por nombre común: *dow*, *nasdaq*,
*oro*, *petróleo*, *bitcoin*...), añade, quita y reordena. Se aplica al instante y se guarda en `settings.local.json`
(no se sube a git), que tiene prioridad sobre la `watchlist` de `config.toml`. Borrar ese fichero devuelve la lista de `config.toml`.
Pulsa una tarjeta para cargar su gráfico. Un símbolo cuyo último tick va más de 5 minutos por detrás del más
reciente se marca como *Mercado cerrado*, y uno que el broker no tiene aparece como *No disponible*.
Usa los nombres exactos de tu broker (en MT5: Ver > Símbolos).

Pinchar una tarjeta carga su gráfico (no hay selector de símbolo ni botón de cargar): para ver un símbolo nuevo,
añádelo primero con **Editar**. Si quitas el mercado que estás viendo, el gráfico carga el primero de la lista.

**Timeframes** (chips sobre el gráfico): M1, M3, M5, M15, H1, H3, H4, H7, H12, 1D y 1W. Cambiar de timeframe recarga el mercado actual.
- MT5 no tiene H7 (solo H1, H2, H3, H4, H6, H8 y H12). H7 se construye agrupando velas de 1 hora, alineadas con la
  medianoche de cada día (hora del servidor): 00-07, 07-14, 14-21 y 21-24, esta última más corta (3 horas).
- Con velas semanales (1W) el sesgo no se recalcula, porque "el día" no existe en ese timeframe: se conserva el último.

Filtro de operativa: con **Bullish** solo se permiten operaciones alcistas (Long), con **Bearish** solo bajistas (Short), y con **No Bias** ambas. La futura capa de ejecución debe consultar `TradeFilter.check(direction)` antes de abrir cualquier trade.

## Requisitos

- Windows con MetaTrader 5 instalado, abierto y con la cuenta iniciada.
- [uv](https://docs.astral.sh/uv/) (`winget install astral-sh.uv`). Descarga Python 3.12 y las dependencias solo.

## Arranque

```powershell
cd C:\Users\claude\DEV\TradingBot
.\scripts\run.ps1              # cuenta por defecto del .env
.\scripts\run.ps1 --demo       # datos sintéticos: la interfaz funciona sin MT5
.\scripts\run.ps1 --profile real
```

Opciones: `--profile`, `--env RUTA`, `--symbol EURUSD`, `--timeframe 5m`, `--theme blanco`, `--demo`.

`run.ps1` hace, por este orden:
1. Lee `tradingbot.env` (ver abajo) y pasa sus valores a la app.
2. Si `APP_AUTO_UPDATE=true`, trae de GitHub el código nuevo (`git pull`) antes de arrancar.
3. Arranca la app con `uv`.

## Configuración (tradingbot.env)

`tradingbot.env`, en la raíz del proyecto, gobierna el arranque y las skills. Es texto `CLAVE=valor`, organizado
en bloques comentados, uno por skill o parte del bot. Cada clave empieza por el nombre de su bloque:

| Bloque | Claves | Para qué |
|---|---|---|
| APP | `APP_AUTO_UPDATE` | Actualizar el código desde GitHub al arrancar (`true`/`false`) |
| UI | `UI_THEME` | Paleta de arranque: `matrix` (por defecto), `negro`, `pizarra` o `blanco` |

Las opciones no usadas se dejan comentadas con `#`, así cambiar de paleta es mover el `#` de línea.
Una variable de entorno con el mismo nombre tiene prioridad sobre el fichero, y `--theme` sobre ambas.
No pongas contraseñas en este fichero: las cuentas de MT5 siguen en `C:\Users\claude\mt5\.env`.

Para desarrolladores: cada skill lee su bloque con `self.settings` (por ejemplo, con `BIAS_MIN_VOTES=2`,
la skill `bias` lee `self.settings.get_int("MIN_VOTES")`). Hay lectores para texto, enteros, decimales, sí/no y listas.

### Cuentas (.env)

Se leen de `C:\Users\claude\mt5\.env` (fuera del repositorio). Formato en `.env.example`:
un bloque `MT5_<PERFIL>_LOGIN / _SERVER / _PASSWORD` por cuenta y `MT5_DEFAULT` con el perfil por defecto.
La contraseña es opcional: si falta, se usa la variable de entorno `MT5_<PERFIL>_PASSWORD` o la sesión ya abierta en el terminal.

Protecciones al conectar:
- Si el terminal está en una cuenta distinta a la del perfil, se cancela.
- Si el perfil se llama `demo` y la cuenta no es demo, se cancela.

### Cuántas velas se cargan

Se piden a MT5 en bloques de 50.000 hasta que no entrega más (tope `max_bars` en `config.toml`).
MT5 limita lo que entrega con *Herramientas > Opciones > Gráficos > Máx. de barras en el gráfico*:
ponlo en **Ilimitado** y reinicia el terminal. El historial disponible depende también del broker.

## Cómo funciona el Bias

Cada regla vota +1 (alcista), -1 (bajista) o 0 (sin opinión). En `config.toml`:

```toml
[bias]
min_votes = 1        # votos mínimos en una dirección
require_all = false  # true: todas las reglas activas deben coincidir

[[bias.rules]]
type = "prev_day_break"
enabled = true
```

- `require_all = false`: hay sesgo si hay al menos `min_votes` votos en una dirección y ninguno en la contraria. Señales opuestas dan **No Bias**.
- `require_all = true`: solo hay sesgo si todas las reglas votan lo mismo.

Las dos reglas incluidas (`prev_day_break`, `above_below_open`) son **solo ejemplos** para ver el sistema funcionando. Sustitúyelas por tus criterios.

El día se determina con la hora del servidor del broker (la que muestra MT5), que puede no coincidir con tu hora local.
El sesgo se calcula al cargar velas y al pulsar *Recalcular sesgo*.

### Añadir una regla nueva

1. En `tradingbot/bias/rules.py`, copia una de las existentes:

```python
@register_rule("mi_regla")
class MiRegla(BiasRule):
    title = "Nombre que verás en la interfaz"

    def evaluate(self, ctx):
        # ctx.last_price, ctx.day_open, ctx.prev_high, ctx.prev_low, ctx.prev_close,
        # ctx.today y ctx.prev (DataFrames de velas), ctx.candles (histórico completo)
        return self.vote(1, "motivo legible")   # +1 alcista, -1 bajista, 0 sin opinión
```

2. Actívala en `config.toml` con `[[bias.rules]]` y `type = "mi_regla"`. Cualquier clave adicional llega a la regla en `self.params`.
3. Añade un test en `tests/test_bias.py`.

## Colores y tema

La paleta de arranque se elige con `UI_THEME` en `tradingbot.env`; por defecto, **matrix** (verde fósforo sobre negro,
con rojo para lo bajista). Las demás: **negro** (fondo negro, texto en azul y verde/rojo para alcista/bajista),
**pizarra** (azul oscuro) y **blanco** (fondo blanco con velas huecas: borde y mecha azul marino, cuerpo blanco las alcistas y gris azulado las bajistas).

El formato de las velas también forma parte de la paleta: `candle_up_fill`, `candle_up_line`, `candle_down_fill` y
`candle_down_line` (relleno y borde/mecha de cada tipo). Si se dejan vacíos, las velas se rellenan con el verde y el
rojo de la paleta; si se rellenan, se pueden hacer velas huecas como en el preset blanco. El editor de colores
los incluye, en la pestaña **Gráfico**, junto con el resto de colores del gráfico: fondo, números del eje (`chart_text`),
rejilla (`chart_grid`), líneas de nivel (`level_high`, `level_low`, `level_open`) y el texto de sus etiquetas
(`level_label`). Todos esos campos son opcionales: vacíos, el gráfico se ve como siempre (números del eje en el
texto secundario, rejilla horizontal muy tenue y niveles en rojo, verde y color de acento). Con `chart_grid` definido, la
rejilla se pinta con ese color exacto y también en vertical.

Cómo personalizarlo:

1. **`tradingbot.env`**: `UI_THEME` elige la paleta de arranque.
2. **Botón "Colores"** de la cabecera: cambia de paleta o retoca cada color con un selector, y se ve al instante.
   *Guardar* deja esa paleta como la de arranque (cambia `UI_THEME` en `tradingbot.env`) y guarda tus colores
   retocados en `theme.local.json` (no se sube a git).
3. **`config.toml`**, sección `[theme]`: colores sueltos (`#RRGGBB`) que se aplican encima de la paleta de arranque.

Los colores retocados (de `config.toml` o del editor) solo se aplican a la paleta para la que se guardaron.

Colores base: `bg`, `panel`, `border`, `text`, `muted`, `accent`, `bull`, `bear`, `warn`, `chart_bg`.
El resto de tonos (fondos de tarjetas, hexágonos, bordes de estado) se derivan de ellos, así que al cambiar uno todo sigue coherente.
Para añadir un preset nuevo, agrégalo a `PRESETS` en `tradingbot/ui/theme.py`.

### Capturas de cada paleta

En la carpeta `screenshots/` hay una captura de la interfaz con cada paleta (con datos sintéticos):
`negro.png`, `pizarra.png`, `matrix.png` y `blanco.png`.

| Negro | Pizarra |
|---|---|
| ![negro](screenshots/negro.png) | ![pizarra](screenshots/pizarra.png) |

| Matrix | Blanco |
|---|---|
| ![matrix](screenshots/matrix.png) | ![blanco](screenshots/blanco.png) |

Para regenerarlas (por ejemplo, tras añadir o retocar una paleta):

```powershell
uv run python scripts\make_screenshots.py                 # todas
uv run python scripts\make_screenshots.py matrix blanco   # solo algunas
```

Las capturas se hacen con la fuente del sistema donde se ejecuta el script, así que en Windows el texto se verá algo distinto.

## Skills (panel de hexágonos)

Cada hexágono del panel derecho es una **skill**: una unidad de trabajo con su propio hilo y su cola de mensajes.
Las skills no se llaman entre sí: se hablan por un **bus de eventos** (se suscriben a temas y publican los suyos).
Así se pueden añadir, quitar o sustituir sin tocar el resto. Cuando una skill envía un mensaje a otra,
la línea entre sus hexágonos se ilumina. Pulsa un hexágono para ver qué escucha y qué publica.

| Skill | Hexágono | Qué hace |
|---|---|---|
| `cortex` | centro | Coordinador. Guarda el Bias vigente y responde a `trade.request` con `trade.verdict` (el filtro de operativa). |
| `feed` | 0 | Conecta con MT5 y carga las velas (`feed.load` -> `candles.loaded`). |
| `bias` | 1 | Evalúa las reglas del sesgo (`candles.loaded` -> `bias.updated`). |
| `quotes` | 5 | Cotizaciones de la watchlist y cifras de la cuenta cada segundo (`quotes.updated`). |

Los huecos del anillo (2, 3 y 4) aparecen como *Libre*. También hay tres satélites pequeños (`aux1`, `aux2`, `aux3`).
Estados: gris azulado en espera, azul activa, brillante trabajando, rojo con error (las demás siguen funcionando).

Flujo actual: `ui -> feed.load -> feed -> candles.loaded -> bias + cortex -> bias.updated -> cortex`.
Pulsa **Long** o **Short** en la tarjeta del Bias para ver a Cortex contestar con `trade.verdict`.

### Añadir una skill nueva

1. Copia `tradingbot/skills/_plantilla.py` con otro nombre (sin guion bajo inicial) y descomenta `@register_skill`.
2. Define `subscribes` (qué escucha), `publishes` (qué dice) y la lógica en `handle(event)`.
3. Actívala en `config.toml`:

```toml
[[skills]]
type = "risk"
slot = 2
```

La plantilla incluye la lista de temas que ya existen y su contenido. Un módulo nuevo en `tradingbot/skills/`
se registra solo; los que empiezan por `_` se ignoran.

## Estructura

```
tradingbot/
  __main__.py        punto de entrada
  config.py          .env (perfiles) y config.toml
  mt5_client.py      conexión y carga de velas (solo lectura)
  demo_data.py       datos sintéticos (--demo)
  core/              bus de eventos y base de las skills
  skills/            feed, quotes, bias, cortex y la plantilla para nuevas skills
  envconfig.py       lectura de tradingbot.env (bloques por skill)
  bias/              modelos, contexto, reglas, motor y filtro de operativa
  ui/                ventana, panel de hexágonos, gráfico de velas, tarjetas, tema
tradingbot.env       configuración de arranque (paleta, actualización automática... y, en adelante, las skills)
config.toml          ajustes y reglas del Bias
scripts/             run.ps1 (arrancar) y sync.ps1 (sincronizar con git)
tests/               pruebas del Bias
```

## Pruebas

```powershell
uv run pytest
```

## Git y actualizaciones

El código vive en el repositorio privado **github.com/lcruzsoria/TradingBot**. Los cambios que prepara Claude se suben
directamente ahí, y tu PC los recibe solo: `run.ps1` hace `git pull` al arrancar (si `APP_AUTO_UPDATE=true`).
Ya no hay zips ni carpetas que copiar.

Configuración inicial (una sola vez), en PowerShell:

```powershell
cd C:\Users\claude\DEV
Rename-Item TradingBot TradingBot_antiguo          # guarda la copia anterior por si acaso
git clone https://github.com/lcruzsoria/TradingBot.git
cd TradingBot
Get-ChildItem -Recurse -Filter *.ps1 | Unblock-File
```

Después, recupera de la copia anterior tus ficheros personales (si existen): `settings.local.json`,
`theme.local.json` y la carpeta `screenshots` con sus PNG.

Para subir **tus** cambios (por ejemplo, tras editar `tradingbot.env` o regenerar las capturas):

```powershell
.\scripts\sync.ps1 "descripcion del cambio"
```

`sync.ps1` confirma tus cambios, trae los de GitHub y sube. `.gitignore` excluye los `.env` con contraseñas
(se versiona solo `tradingbot.env`, que no lleva secretos), y `sync.ps1` se niega a subir un `.env` si lo detecta.
