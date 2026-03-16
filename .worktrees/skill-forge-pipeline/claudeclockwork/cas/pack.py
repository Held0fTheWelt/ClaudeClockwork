"""Phase 36 — Pack CAS refs + missing objects for worker transport; verify integrity on unpack."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from claudeclockwork.cas.store import get, exists
from claudeclockwork.workers.artifact_transport import pack_bundle
import tempfile


def pack_cas_refs(
    cas_root: Path | str,
    refs: list[str],
    out_zip: Path | str,
) -> dict[str, Any]:
    """Pack CAS objects for refs into zip; include only those present. Returns manifest of refs included."""
    cas_root = Path(cas_root).resolve()
    out_zip = Path(out_zip).resolve()
    staging = Path(tempfile.mkdtemp())
    try:
        included: list[str] = []
        for h in refs:
            data = get(cas_root, h)
            if data is not None:
                (staging / h).write_bytes(data)
                included.append(h)
        pack_bundle(staging, out_zip, redact=False)
        return {"refs_requested": len(refs), "refs_included": included}
    finally:
        import shutil
        shutil.rmtree(staging, ignore_errors=True)
