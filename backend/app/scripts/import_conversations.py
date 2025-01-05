import argparse
import asyncio
import csv
from pathlib import Path

from app.client.api_client import APIClient


async def import_conversations(csv_path: Path, base_url: str = "http://localhost:8000"):
    """Import conversations from CSV file using the API client."""
    print(f"Importing conversations from {csv_path}")

    async with APIClient(base_url=base_url) as client:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            imported = 0

            for row in reader:
                try:
                    conversation = await client.create_conversation(
                        question=row["question"].strip(), answer=row["answer"].strip()
                    )
                    print(f"Imported conversation {conversation.id}")
                    imported += 1
                except Exception as e:
                    print(f"Error importing conversation: {e}")
                    continue

            print(f"Successfully imported {imported} conversations")


def main():
    """Main entry point for the import script."""
    parser = argparse.ArgumentParser(description="Import conversations from CSV file")
    parser.add_argument(
        "--file",
        type=Path,
        help="Path to CSV file (default: train.csv in project root)",
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL for the API (default: http://localhost:8000)",
    )

    args = parser.parse_args()

    # If no file specified, use default train.csv in project root
    if not args.file:
        args.file = Path(__file__).parent.parent.parent / "train.csv"

    if not args.file.exists():
        print(f"Error: Could not find {args.file}")
        return

    asyncio.run(import_conversations(args.file, args.url))


if __name__ == "__main__":
    main()
