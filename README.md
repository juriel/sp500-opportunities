# S&P 500 Opportunities

Scripts en Python para analizar el S&P 500 y detectar oportunidades de inversión.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> **Nota:** `TA-Lib` requiere la librería C instalada en el sistema. Ver sección [Dependencias del sistema](#dependencias-del-sistema).

## Uso

```bash
python main.py                        # lista los comandos disponibles
python main.py <comando> --help       # ayuda del comando
```

### Opciones comunes a todos los comandos

| Opción | Descripción |
|--------|-------------|
| `--pretty` | Muestra los resultados en tabla formateada |
| `--output ARCHIVO` | Exporta a `.csv` o `.xlsx` (la extensión decide el formato) |

## Comandos

### `download`

Descarga el listado de componentes del S&P 500 con peso en el índice, precio y variación del día.

```bash
python main.py download                        # todas las acciones
python main.py download -n 20                  # primeras 20
python main.py download -n 20 --reverse        # últimas 20 (menor peso)
python main.py download -n 20 --pretty         # tabla formateada
python main.py download --output sp500.csv     # exportar a CSV
python main.py download --output sp500.xlsx    # exportar a Excel
```

| Parámetro | Descripción |
|-----------|-------------|
| `-n, --number N` | Número de acciones a mostrar |
| `--reverse` | Invierte el orden (de menor a mayor peso) |

---

### `indicators`

Calcula más de 55 indicadores técnicos usando TA-Lib. Acepta uno o varios tickers separados por coma.

```bash
python main.py indicators NVDA                          # un ticker
python main.py indicators NVDA,IBM,TSLA --pretty        # varios tickers, tabla formateada
python main.py indicators NVDA --period 2y              # período histórico personalizado
python main.py indicators NVDA,IBM --output analisis.xlsx  # una hoja por ticker en Excel
python main.py indicators NVDA,IBM --output analisis.csv   # CSV con columna ticker
```

| Parámetro | Descripción |
|-----------|-------------|
| `tickers` | Ticker(s) separados por coma: `NVDA,IBM,TSLA` |
| `--period` | Período histórico: `3mo`, `6mo`, `1y` (default), `2y`, `5y` |

**Indicadores calculados:**

| Categoría | Indicadores |
|-----------|-------------|
| Tendencia | SMA 20/50/200, EMA 9/12/21/26/50, DEMA, TEMA, KAMA, T3, HT_TRENDLINE, HT_TRENDMODE |
| Momentum | RSI, MACD, STOCH, STOCHRSI, WILLR, CCI, CMO, AROON, ULTOSC, ROC, TRIX, PPO, BOP, ADX, PLUS/MINUS DI, MFI |
| Volatilidad | Bollinger Bands (upper/mid/lower/width), ATR, NATR, TRANGE |
| Volumen | OBV, AD, ADOSC |
| Ciclos | HT_DCPERIOD, HT_DCPHASE, HT_SINE, HT_LEADSINE |
| Estadística | LINEARREG_SLOPE, STDDEV, BETA, TSF, VAR |
| Patrones de velas | DOJI, HAMMER, ENGULFING, MORNING/EVENING STAR, 3 WHITE SOLDIERS, 3 BLACK CROWS, HARAMI, SHOOTING STAR |

---

## Estructura

```
sp500-opportunities/
├── main.py             # Entry point
├── scripts/            # Un archivo por análisis
│   ├── download.py
│   └── indicators.py
├── utils/
│   ├── sp500.py        # Descarga la lista del S&P 500
│   └── output.py       # Salida: consola, CSV, Excel
└── data/               # Datos locales (ignorados por git)
```

## Dependencias del sistema

**TA-Lib** requiere la librería C instalada antes de `pip install TA-Lib`. No está en los repos de Fedora, compilar desde fuente:

```bash
wget https://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib && ./configure --prefix=/usr && make && sudo make install
```

## Fuentes de datos

- **slickcharts.com** — lista actualizada de componentes y pesos del S&P 500
- **yfinance** — precios históricos y datos OHLCV
- **TA-Lib** — cálculo de indicadores técnicos
