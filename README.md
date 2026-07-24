# S&P 500 Opportunities

Scripts en Python para analizar el S&P 500 y detectar oportunidades de inversión.

## Setup

```bash
# Crear y activar el entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Para desarrollo (incluye linting)
pip install -r requirements-dev.txt
```

## Estructura

```
sp500-opportunities/
├── scripts/        # Scripts de análisis listos para ejecutar
├── utils/          # Funciones auxiliares reutilizables
├── data/
│   ├── raw/        # Datos descargados (ignorados por git)
│   └── cache/      # Caché de peticiones (ignorado por git)
└── output/         # Resultados generados
```

## Scripts disponibles

| Script | Descripción |
|--------|-------------|
| *(próximamente)* | |

## Fuentes de datos

- **yfinance** — precios históricos y datos fundamentales
- **Wikipedia** — lista actualizada de componentes del S&P 500
