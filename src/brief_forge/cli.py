from .config import settings
from .pipeline import run_generation

def main():
    import argparse
    parser = argparse.ArgumentParser(
        prog="brief-forge",
        description="Generate a technology news presentation with private speaker notes."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("generate", help="Collect news and generate a PPTX presentation")
    args = parser.parse_args()
    if args.command == "generate":
        try:
            run_generation(settings)
        except KeyboardInterrupt:
            print("\nCancelled.")
            raise SystemExit(130)
        except Exception as exc:
            print(f"ERROR: {exc}")
            raise SystemExit(1)
