import argparse
import sys

from scripts import download


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sp500",
        description="Herramientas para analizar el S&P 500 y encontrar oportunidades.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="<comando>")

    download.register(subparsers)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        print("Comandos disponibles:\n")
        for name, p in parser._subparsers._group_actions[0].choices.items():
            print(f"  {name:<20} {p.description or ''}")
        print(f"\nUsa: python main.py <comando> --help")
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
