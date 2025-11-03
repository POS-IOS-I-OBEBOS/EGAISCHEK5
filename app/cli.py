"""Command line entry point for the barcode reader utility."""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Iterable, List

from app.barcode_reader import BarcodeReader
from app.logging_utils import configure_logging


logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read barcodes from a local image using Aspose Barcode Cloud."
    )
    parser.add_argument("image", type=Path, help="Path to the image that contains barcodes")
    parser.add_argument(
        "--type",
        dest="barcode_types",
        action="append",
        help="Limit recognition to the provided symbology (can be passed multiple times)",
    )
    parser.add_argument(
        "--preset",
        help="Optional Aspose recognition preset (e.g. HighPerformance, HighQuality)",
    )
    parser.add_argument("--base-url", help="Override the Aspose Cloud API base url", default=None)
    parser.add_argument(
        "--client-id",
        default=os.getenv("ASPOSE_CLIENT_ID"),
        help="Aspose Cloud client id. Falls back to the ASPOSE_CLIENT_ID environment variable.",
    )
    parser.add_argument(
        "--client-secret",
        default=os.getenv("ASPOSE_CLIENT_SECRET"),
        help=(
            "Aspose Cloud client secret. Falls back to the ASPOSE_CLIENT_SECRET environment "
            "variable."
        ),
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help=(
            "Path to the log file. Defaults to barcode_reader.log in the current working "
            "directory."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine readable JSON instead of a human friendly table.",
    )
    return parser


def _ensure_credentials(client_id: str | None, client_secret: str | None) -> None:
    if not client_id or not client_secret:
        raise SystemExit(
            "Missing credentials. Either pass --client-id/--client-secret or set "
            "ASPOSE_CLIENT_ID/ASPOSE_CLIENT_SECRET."
        )
    logger.debug("Credentials verified (client id provided: %s, client secret provided: %s)", bool(client_id), bool(client_secret))


def _format_table(results: Iterable[dict]) -> str:
    rows: List[str] = []
    for item in results:
        value = item.get("value", "")
        symbology = item.get("symbology", "")
        confidence = item.get("confidence")
        confidence_str = f" ({confidence:.2%})" if isinstance(confidence, (int, float)) else ""
        rows.append(f"{symbology}: {value}{confidence_str}")
    return "\n".join(rows) if rows else "No barcodes found."


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    log_path = configure_logging(args.log_file)
    logger.info("Log file initialised at %s", log_path)
    logger.info("Starting barcode recognition for image %s", args.image)
    if args.barcode_types:
        logger.debug("Barcode type filters: %s", ", ".join(args.barcode_types))
    if args.preset:
        logger.debug("Recognition preset: %s", args.preset)
    if args.base_url:
        logger.debug("Using custom base URL: %s", args.base_url)

    _ensure_credentials(args.client_id, args.client_secret)

    with BarcodeReader(
        client_id=args.client_id,
        client_secret=args.client_secret,
        base_url=args.base_url,
    ) as reader:
        results = reader.scan_image(
            args.image,
            barcode_types=args.barcode_types,
            preset=args.preset,
        )

    logger.info("Recognition finished. %d barcode(s) found.", len(results))

    payload = [
        {
            "value": item.value,
            "symbology": item.symbology,
            "confidence": item.confidence,
        }
        for item in results
    ]

    if args.json:
        logger.debug("Writing JSON payload to stdout")
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0

    logger.debug("Writing table output to stdout")
    sys.stdout.write(_format_table(payload) + "\n")
    else:
        logger.debug("Writing table output to stdout")
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(_format_table(payload) + "\n")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
