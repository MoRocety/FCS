"""Stateless signed continuation of the exact catalog/shortlist/rule search."""

import hashlib
import json
from flask import current_app
from itsdangerous import URLSafeSerializer, BadData
from .scheduling import generate


def generate_batch(
    sections, minimum, maximum, required, rules, catalog_revision, continuation=None
):
    fingerprint = hashlib.sha256(
        json.dumps(
            {
                "revision": catalog_revision,
                "sections": [s["id"] for s in sections],
                "minimum": minimum,
                "maximum": maximum,
                "required": sorted(required),
                "rules": rules,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    signer = URLSafeSerializer(current_app.secret_key, salt="fcs-schedule-search-v1")
    frontier = None
    if continuation is not None:
        if not isinstance(continuation, str) or not 1 <= len(continuation) <= 65536:
            raise ValueError("Invalid search continuation. Start a new search.")
        try:
            cursor = signer.loads(continuation)
        except BadData as exc:
            raise ValueError(
                "Invalid search continuation. Start a new search."
            ) from exc
        if not isinstance(cursor, dict) or cursor.get("fingerprint") != fingerprint:
            raise ValueError("Search inputs changed. Start a new search.")
        frontier = cursor["frontier"]
    result = generate(
        sections,
        minimum,
        maximum,
        required,
        rules=rules,
        continuation=frontier,
        limit=current_app.config.get("SCHEDULE_BATCH_LIMIT", 50),
        budget=current_app.config.get("SCHEDULE_NODE_BUDGET", 100000),
    )
    result["continuation"] = (
        signer.dumps({"fingerprint": fingerprint, "frontier": result["continuation"]})
        if result["continuation"]
        else None
    )
    return result
