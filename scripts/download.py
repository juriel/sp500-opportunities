from utils.sp500 import get_sp500_components
from utils.output import show


def register(subparsers):
    p = subparsers.add_parser(
        "download",
        help="Descarga el listado de componentes del S&P 500 desde slickcharts.com",
        description=(
            "Obtiene el listado actualizado de las 500 empresas del S&P 500 "
            "con su peso en el índice, precio actual y variación del día."
        ),
    )
    p.add_argument(
        "-n", "--number",
        type=int,
        default=None,
        metavar="N",
        help="Número de acciones a mostrar (por defecto: todas)",
    )
    p.add_argument(
        "--reverse",
        action="store_true",
        help="Invierte el orden (de menor a mayor peso en el índice)",
    )
    p.add_argument(
        "--pretty",
        action="store_true",
        help="Muestra los resultados en tabla formateada",
    )
    p.add_argument(
        "--output",
        metavar="ARCHIVO",
        help="Exporta los resultados a un archivo (.csv o .xlsx)",
    )
    p.set_defaults(func=run)


def run(args):
    df = get_sp500_components()

    if args.reverse:
        df = df.iloc[::-1].reset_index(drop=True)

    if args.number is not None:
        df = df.head(args.number)

    show(df, args)
