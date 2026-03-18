"""CLI entry point for TendedLoop Arena SDK."""

import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        from .demo import run_demo_server

        port = 7860
        if len(sys.argv) > 2:
            port = int(sys.argv[2])
        run_demo_server(port=port)
    else:
        print("Usage: python -m tendedloop_agent demo [port]")
        print("  Starts a local Arena sandbox server for development")
        sys.exit(1)


if __name__ == "__main__":
    main()
