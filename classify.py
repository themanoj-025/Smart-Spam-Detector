#!/usr/bin/env python3
"""
Spam Email Classifier — CLI Tool

Classify any email text as Spam or Ham directly from the command line.

Usage:
    python classify.py "Your email text here"
    python classify.py --file email.txt
    echo "Your email text" | python classify.py
"""

import sys
import argparse
from pathlib import Path

# Ensure we can import from src
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.pipeline.prediction_pipeline import PredictionPipeline


def classify(text: str) -> None:
    """Classify a single email and print the result."""
    try:
        pipeline = PredictionPipeline(load_models=True)
        result = pipeline.predict_single_email(text)

        prediction = result["prediction"]
        confidence = result.get("confidence")

        confidence_str = f"(confidence: {confidence:.1f}%)" if confidence is not None else ""
        if prediction == "Spam":
            print(f"\n  [SPAM]  PREDICTION: SPAM  {confidence_str}\n")
        else:
            print(f"\n  [HAM]   PREDICTION: HAM (Safe)  {confidence_str}\n")

    except FileNotFoundError as e:
        print(f"\n  [ERROR]  {e}", file=sys.stderr)
        print("\n  Run the training pipeline first:")
        print("    python -m src.pipeline.training_pipeline\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n  ❌  Error: {e}\n", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Classify an email as Spam or Ham using a trained SVM model.",
        epilog="Examples:\n"
               "  python classify.py \"Congratulations! You won a prize!\"\n"
               "  python classify.py --file email.txt\n"
               "  cat email.txt | python classify.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "text",
        nargs="?",
        help="Email text to classify (or pipe input via stdin)",
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Read email text from a file",
    )

    args = parser.parse_args()

    # Priority: --file > positional arg > stdin
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read().strip()
        except FileNotFoundError:
            print(f"  [ERROR]  File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
    elif args.text:
        text = args.text
    elif not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    else:
        parser.print_help()
        print("\n  [ERROR]  Please provide email text, a file, or pipe input.\n")
        sys.exit(1)

    if not text:
        print("  [ERROR]  No text provided to classify.\n")
        sys.exit(1)

    classify(text)


if __name__ == "__main__":
    main()
