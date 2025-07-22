import argparse
import sys


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Knowledge Management System CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add index subcommand
    index_parser = subparsers.add_parser('index', help='Index org files into ChromaDB')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Dispatch to appropriate handler
    if args.command == 'index':
        print("Indexing...")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
