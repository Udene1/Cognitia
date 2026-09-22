"""Observe the live Cashflow OS environment during every Cognitia CI run.

This is an observation boundary, not a benchmark. The script records what the
external environment returned and then lets Cognitia's existing deterministic
claim extractor operate on those observations. It does not encode expected
claims, outcomes, or conclusions.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from cognitia.document_claims import DocumentClaimExtractor
from cognitia.environment import EnvironmentObservation


DEFAULT_URL = "https://cashflow-os-silk.vercel.app/api/environment/observations"


def fetch_environment(url: str) -> dict:
    query = urlencode({"limit": "200"})
    request = Request(
        f"{url}?{query}",
        headers={"Accept": "application/json", "User-Agent": "Cognitia-CI"},
    )
    with urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"Cashflow observation feed returned HTTP {response.status}")
        payload = json.load(response)

    if not isinstance(payload, dict) or not isinstance(payload.get("observations"), list):
        raise RuntimeError("Cashflow observation feed did not return an observation list")
    return payload


def main() -> None:
    url = os.environ.get("CASHFLOW_OBSERVATION_URL", DEFAULT_URL)
    payload = fetch_environment(url)
    observations = payload["observations"]

    cognitive_observations = tuple(
        EnvironmentObservation(
            id=str(item["id"]),
            source=str(item.get("source", "cashflow-os")),
            content=str(item.get("content", "")),
        )
        for item in observations
    )

    extractor = DocumentClaimExtractor()
    extracted = tuple(
        claim
        for observation in cognitive_observations
        for claim in extractor.extract(observation)
    )

    artifact = {
        "environment": {
            "source": payload.get("source"),
            "url": url,
            "nextSince": payload.get("nextSince"),
        },
        "observation_count": len(observations),
        "observations": observations,
        "cognition": {
            "claim_count": len(extracted),
            "claims": [repr(claim) for claim in extracted],
        },
    }

    output = Path(".ci/cashflow-observation.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")

    print("CASHFLOW_ENVIRONMENT_OBSERVED")
    print(f"observation_count={len(observations)}")
    print(f"claim_count={len(extracted)}")
    print(f"next_since={payload.get('nextSince')}")
    print(f"artifact={output}")


if __name__ == "__main__":
    main()
