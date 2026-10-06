# TradingBot

Bot de trading con interfaz gráfica sobre MetaTrader 5. Esta primera versión incluye dos tareas y **no opera**:
no existe ninguna llamada para enviar órdenes, solo lectura de datos.

La interfaz sigue el estilo de la referencia visual: azul pizarra oscuro, paneles planos con borde fino,
tarjetas de mercado, gráfico de velas verde azulado/coral y, a la derecha, el sesgo del día.

| Tarea | Qué hace |
|---|---|
| Conexión y velas | Conecta con MT5 usando la cuenta del `.env` y carga todas las velas posibles en 1m, 3m, 5m o 15m (por defecto 15m). |
| Bias | Evalúa las reglas y decide el sesgo del día: **Bullish**, **Bearish** o **No Bias**. Se muestra en un recuadro fijo de la interfaz. |

Cabecera: estado de la conexión, cuenta, saldo/equity, P&L abierto, mercados con precio en vivo y hora del último tick (hora del servidor).

Panel **Mercados**: cotizaciones de solo lectura de la `watchlist` de `config.toml` (se refrescan cada segundo).
Pulsa una tarjeta para cargar su gráfico. Un símbolo cuyo último tick va más de 5 minutos por detrás del más
reciente se marca como *Mercado cerrado*, y uno que el broker no tiene aparece como *No disponible*.
Usa los nombres exactos de tu broker (en MT5: Ver > Símbolos).

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

Opciones: `--profile`, `--env RUTA`, `--symbol EURUSD`, `--timeframe 5m`, `--demo`.

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

Por defecto la interfaz usa el preset **negro**: fondo negro, texto en azul y verde/rojo para alcista/bajista
(velas, sesgo, P&L y el precio de cada tarjeta, que se tiñe según el último tick suba o baje).
El otro preset es **pizarra** (azul oscuro).

Tres formas de personalizarlo, de menor a mayor prioridad:

1. **`config.toml`**, sección `[theme]`: elige `preset` y sobrescribe colores sueltos en formato `#RRGGBB`.
2. **Botón "Colores"** de la cabecera: cambia cada color con un selector y se ve al instante.
   Pulsa *Guardar* para conservarlo; se escribe en `theme.local.json` (no se sube a git).
3. **`theme.local.json`**: se puede editar a mano. Borrarlo devuelve el tema de `config.toml`.

Colores base: `bg`, `panel`, `border`, `text`, `muted`, `accent`, `bull`, `bear`, `warn`, `chart_bg`.
El resto de tonos (fondos de tarjetas, hexágonos, bordes de estado) se derivan de ellos, así que al cambiar uno todo sigue coherente.
Para añadir un preset nuevo, agrégalo a `PRESETS` en `tradingbot/ui/theme.py`.

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
  bias/              modelos, contexto, reglas, motor y filtro de operativa
  ui/                ventana, panel de hexágonos, gráfico de velas, tarjetas, tema
config.toml          ajustes y reglas del Bias
scripts/             run.ps1 (arrancar) y sync.ps1 (sincronizar con git)
tests/               pruebas del Bias
```

## Pruebas

```powershell
uv run pytest
```

## Git

Primera vez (crea antes un repositorio **privado y vacío** llamado TradingBot en GitHub):

```powershell
cd C:\Users\claude\DEV\TradingBot
git init -b main
git add -A
git commit -m "TradingBot: estructura inicial"
git remote add origin https://github.com/TU_USUARIO/TradingBot.git
git push -u origin main
```

Después, para sincronizar cualquier cambio:

```powershell
.\scripts\sync.ps1 "descripcion del cambio"
```

`.gitignore` excluye los `.env`, y `sync.ps1` se niega a subir uno si lo detecta dentro del repositorio.
