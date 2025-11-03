"""High level helpers around the Aspose Barcode Cloud SDK."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional
import base64

try:  # pragma: no cover - import resolution depends on SDK version
    from aspose_barcode_cloud import (  # type: ignore
        ApiClient,
        ApiConfiguration,
        BarcodeApi,
        ScanBase64Options,
        ScanBase64Request,
    )

    _NEW_SDK = True
except ImportError:  # pragma: no cover
    from aspose_barcode_cloud import (  # type: ignore
        ApiClient,
        BarcodeApi,
        Configuration as ApiConfiguration,
        PostBarcodeRecognizeFromUrlOrContentRequest,
    )

    _NEW_SDK = False


@dataclass
class RecognizedBarcode:
    """A simple representation of the recognition result."""

    value: str
    symbology: str
    confidence: Optional[float] = None


class BarcodeReader:
    """Wraps the Aspose Barcode Cloud SDK to read codes from local images."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        *,
        base_url: Optional[str] = None,
    ) -> None:
        configuration = self._build_configuration(client_id, client_secret, base_url)
        self._api_client = ApiClient(configuration)
        self._barcode_api = BarcodeApi(self._api_client)

    @staticmethod
    def _build_configuration(
        client_id: str, client_secret: str, base_url: Optional[str]
    ) -> ApiConfiguration:
        if _NEW_SDK:
            configuration = ApiConfiguration(client_id=client_id, client_secret=client_secret)
            if base_url:
                configuration.api_base_url = base_url
            return configuration

        configuration = ApiConfiguration()
        if hasattr(configuration, "client_id"):
            configuration.client_id = client_id
        elif hasattr(configuration, "app_sid"):
            configuration.app_sid = client_id
        else:  # pragma: no cover - defensive
            raise AttributeError("Unsupported SDK configuration: client id field not found")

        if hasattr(configuration, "client_secret"):
            configuration.client_secret = client_secret
        elif hasattr(configuration, "app_key"):
            configuration.app_key = client_secret
        else:  # pragma: no cover - defensive
            raise AttributeError("Unsupported SDK configuration: client secret field not found")

        if base_url:
            if hasattr(configuration, "api_base_url"):
                configuration.api_base_url = base_url
            elif hasattr(configuration, "base_url"):
                configuration.base_url = base_url
        return configuration

    def scan_image(
        self,
        image_path: Path | str,
        *,
        barcode_types: Optional[Iterable[str]] = None,
        preset: Optional[str] = None,
    ) -> List[RecognizedBarcode]:
        """Recognise barcodes from a local image.

        Args:
            image_path: Path to the image that contains barcodes.
            barcode_types: Optional iterable with the list of symbologies to search for.
            preset: Optional Aspose preset name (e.g. ``HighPerformance``).
        """

        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")

        image_bytes = path.read_bytes()

        if _NEW_SDK:
            return self._scan_with_new_sdk(image_bytes, barcode_types, preset)
        return self._scan_with_legacy_sdk(image_bytes, barcode_types, preset)

    # ------------------------------------------------------------------
    def _scan_with_new_sdk(
        self,
        image_bytes: bytes,
        barcode_types: Optional[Iterable[str]],
        preset: Optional[str],
    ) -> List[RecognizedBarcode]:
        assert _NEW_SDK
        options = ScanBase64Options(
            image=base64.b64encode(image_bytes).decode("ascii"),
            barcode_types=list(barcode_types or []),
        )
        if preset:
            options.preset = preset

        request = ScanBase64Request(scan_options=options)
        response = self._barcode_api.scan_base64(request)
        results = getattr(response, "barcodes", None) or getattr(response, "barcode_list", [])
        return [
            RecognizedBarcode(
                value=getattr(item, "barcode_value", ""),
                symbology=getattr(item, "type", getattr(item, "code_type_name", "")),
                confidence=getattr(item, "confidence", None),
            )
            for item in results
        ]

    def _scan_with_legacy_sdk(
        self,
        image_bytes: bytes,
        barcode_types: Optional[Iterable[str]],
        preset: Optional[str],
    ) -> List[RecognizedBarcode]:
        assert not _NEW_SDK
        types_param = None
        if barcode_types:
            types_param = ",".join(barcode_types)

        kwargs = {"type": types_param, "file": image_bytes}
        if preset:
            kwargs["preset"] = preset

        request = PostBarcodeRecognizeFromUrlOrContentRequest(**kwargs)
        response = self._barcode_api.post_barcode_recognize_from_url_or_content(request)
        results = getattr(response, "barcodes", None) or getattr(response, "barcode_list", [])
        return [
            RecognizedBarcode(
                value=getattr(item, "barcode_value", ""),
                symbology=getattr(item, "type", getattr(item, "code_type_name", "")),
                confidence=getattr(item, "confidence", None),
            )
            for item in results
        ]

    def close(self) -> None:
        self._api_client.close()

    def __enter__(self) -> "BarcodeReader":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
