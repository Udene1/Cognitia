"""Incrementally observe the live Cashflow OS environment.

The Cashflow endpoint exposes a timestamp boundary (since/nextSince).
Cognitia treats that boundary as acquisition state, while SQLite remains the
append-only observation memory. A moving API window must never cause older
observations or claims to disappear from Cognitia's durable state.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from cognitia.document_claims import DocumentClaimExtractor
from cognitia.environment import EnvironmentObservation
from cognitia.memory.observation_sqlite import SQLiteObservationStore
from cognitia.observation import Observation


DEFAULT_URL = "https://cashflow-os-silk.vercel.app/api/environment/observations"
ENVIRONMENT = "cashflow-os"
BATCH_LIMIT = 200


def fetch_environment(url: str, *, since: str | None) -> dict:
    params = {"limit": str(BATCH_LIMIT)}
    if since is not None:
        params["since"] = since
    request = Request(
        f"{url}?{urlencode(params)}",
        headers={"Accept": "application/json", "User-Agent": "Cognitia-CI"},
    )
    with urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"Cashflow observation feed returned HTTP {response.status}")
        payload = json.load(response)

    if not isinstance(payload, dict) or not isinstance(payload.get("observations"), list):
        raise RuntimeError("Cashflow observation feed did not return an observation list")
    return payload


def to_observation(item: dict, url: str) -> Observation:
    return Observation.create(
        environment=str(item.get("source", ENVIRONMENT)),
        kind=str(item.get("kind", "environment.observation")),
        subject=str(item["id"]),
        payload=json.dumps(item, ensure_ascii=False, sort_keys=True),
        source_uri=url,
        observed_at=str(item.get("observedAt")) if item.get("observedAt") is not None else None,
        metadata=tuple(
            (str(key), str(value))
            for key, value in sorted((item.get("metadata") or {}).items())
        ),
    )


def cognitive_observation(item: Observation) -> EnvironmentObservation:
    raw = json.loads(item.payload)
    return EnvironmentObservation(
        id=str(raw["id"]),
        source=str(raw.get("source", ENVIRONMENT)),
        content=str(raw.get("content", "")),
    )


def main() -> None:
    url = os.environ.get("CASHFLOW_OBSERVATION_URL", DEFAULT_URL)
    persistence_root = Path(os.environ.get("COGNITIA_PERSISTENCE_ROOT", ".ci/persistence"))
    persistence_root.mkdir(parents=True, exist_ok=True)
    observation_store_path = persistence_root / "observations.sqlite"

    batches: list[dict] = []
    acquired_ids: set[str] = set()

    with SQLiteObservationStore(observation_store_path) as store:
        since = store.latest_observed_at(environment=ENVIRONMENT)
        initial_since = since

        while True:
            payload = fetch_environment(url, since=since)
            batch = payload["observations"]
            next_since = payload.get("nextSince")
            batches.append(
                {
                    "since": since,
                    "observation_count": len(batch),
                    "nextSince": next_since,
                }
            )

            for item in batch:
                observation = to_observation(item, url)
                before = _contains(store, observation.id)
                store.ingest(observation)
                if not before:
                    acquired_ids.add(observation.id)

            if not batch or len(batch) < BATCH_LIMIT:
                break
            if not isinstance(next_since, str) or not next_since:
                break
            if since is not None and next_since <= since:
                break
            since = next_since

        retained = store.by_environment(ENVIRONMENT)
        retained_count = len(retained)
        final_since = store.latest_observed_at(environment=ENVIRONMENT)

        extractor = DocumentClaimExtractor()
        extracted = tuple(
            claim
            for observation in (cognitive_observation(item) for item in retained)
            for claim in extractor.extract(observation)
        )

    artifact = {
        "environment": {
            "source": ENVIRONMENT,
            "url": url,
            "acquisition": {
                "initial_since": initial_since,
                "final_since": final_since,
                "batches": batches,
                "new_observations_acquired": len(acquired_ids),
            },
        },
        "observation_count": retained_count,
        "observations": [json.loads(item.payload) for item in retained],
        "cognition": {
            "claim_count": len(extracted),
            "claims": [repr(claim) for claim in extracted],
        },
    }

    output = Path(".ci/cashflow-observation.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")

    print("CASHFLOW_ENVIRONMENT_OBSERVED")
    print(f"new_observations_acquired={len(acquired_ids)}")
    print(f"durable_observation_count={retained_count}")
    print(f"claim_count={len(extracted)}")
    print(f"initial_since={initial_since}")
    print(f"final_since={final_since}")
    print(f"batches={len(batches)}")
    print(f"artifact={output}")


def _contains(store: SQLiteObservationStore, observation_id: str) -> bool:
    try:
        store.get(observation_id)
    except KeyError:
        return False
    return True


if __name__ == "__main__":
    main()
