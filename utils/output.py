import sys
from pathlib import Path

import pandas as pd
from tabulate import tabulate


def show(df: pd.DataFrame, args) -> None:
    if getattr(args, "output", None):
        _export(df, args.output)
    elif getattr(args, "pretty", False):
        _print_table(df)
    else:
        print(df.to_string(index=False))


def _print_table(df: pd.DataFrame, tablefmt: str = "rounded_outline") -> None:
    print(tabulate(df, headers="keys", tablefmt=tablefmt, showindex=False))


def _export(df: pd.DataFrame, filepath: str) -> None:
    path = Path(filepath)
    ext = path.suffix.lower()
    path.parent.mkdir(parents=True, exist_ok=True)

    if ext == ".csv":
        df.to_csv(path, index=False)
    elif ext in (".xlsx", ".xls"):
        df.to_excel(path, index=False, engine="openpyxl")
    else:
        print(f"Error: extensión '{ext}' no soportada. Usa .csv o .xlsx", file=sys.stderr)
        sys.exit(1)

    print(f"Guardado en {path}")
