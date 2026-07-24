# S&P 500 Opportunities — Guía del proyecto

## Arquitectura

- `main.py` — entry point. Usa `argparse` con subcomandos para despachar a los scripts hijos.
- `scripts/` — un archivo por análisis. Cada script expone `register(subparsers)` y `run(args)`.
- `utils/sp500.py` — descarga la lista de componentes del S&P 500 desde slickcharts.com.
- `utils/output.py` — salida unificada: consola plain, tabla con tabulate, o exportar a archivo.

## Convención de scripts hijos

Cada script en `scripts/` debe seguir este patrón:

```python
from utils.output import show

def register(subparsers):
    p = subparsers.add_parser("nombre", help="...", description="...")
    # argumentos propios del script
    p.add_argument("--pretty", action="store_true", help="Tabla formateada en consola")
    p.add_argument("--output", metavar="ARCHIVO", help="Exportar a .csv o .xlsx")
    p.set_defaults(func=run)

def run(args):
    # lógica del script → produce un DataFrame
    show(df, args)
```

Registrarlo en `main.py`:
```python
from scripts import nuevo_script
nuevo_script.register(subparsers)
```

## Parámetros comunes (todos los scripts los incluyen)

| Parámetro | Descripción |
|-----------|-------------|
| `--pretty` | Muestra resultado en tabla formateada con `tabulate` |
| `--output ARCHIVO` | Exporta a archivo; la extensión decide el formato (`.csv` o `.xlsx`) |

Si se usa `--output`, se ignora `--pretty`.

## Fuente de datos

- Lista S&P 500: `https://www.slickcharts.com/sp500` (scraping HTML con `requests` + `beautifulsoup4`)
- Datos históricos y fundamentales: `yfinance`

## Entorno

```bash
source venv/bin/activate
python main.py <comando> --help
```

## Dependencias del sistema

**TA-Lib** requiere la librería C instalada antes de `pip install TA-Lib`.
No está en los repos de Fedora — compilar desde fuente:

```bash
wget https://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib && ./configure --prefix=/usr && make && sudo make install
```
