# S&P 500 Opportunities

Scripts en Python para analizar el S&P 500 y detectar oportunidades de inversión.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

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

## Estructura

```
sp500-opportunities/
├── main.py             # Entry point
├── scripts/            # Un archivo por análisis
├── utils/
│   ├── sp500.py        # Descarga la lista del S&P 500
│   └── output.py       # Salida: consola, CSV, Excel
└── data/               # Datos locales (ignorados por git)
```

## Fuentes de datos

- **slickcharts.com** — lista actualizada de componentes y pesos del S&P 500
- **yfinance** — precios históricos y datos fundamentales
