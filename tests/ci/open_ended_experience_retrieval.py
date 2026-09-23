"""Run the live open-ended experience retrieval experiment.

No history is supplied to Cognitia by the experiment. It asks a question, lets
the retriever decide which durable observations are relevant, and then lets the
research controller choose an investigation from the retrieved experience plus
current evidence.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from cognitia.document_claims import DocumentClaimExtractor, ExtractedClaim
from cognitia.environment import EnvironmentObservation
from cognitia.experience_retrieval import ObservationExperienceRetriever
from cognitia.memory.observation_sqlite import SQLiteObservationStore
from cognitia.observation import Observation
from cognitia.research_autonomy import ResearchActionController


DEFAULT_URL = "https://cashflow-os-silk.vercel.app/api/environment/observations"
ENVIRONMENT = "cashflow-os"
BATCH_LIMIT = 200
CURRENT_LIMIT = 20
QUESTIONS = (
    "Which prior prospect-touch events correspond to later stage transitions?",
    "What evidence explains why a prospect's stage changed after an earlier interaction?",
)


def fetch_environment(url: str, *, since: str | None, limit: int) -> dict:
    params = {"limit": str(limit)}
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
        observed_at=str(item["observedAt"]) if item.get("observedAt") is not None else None,
        metadata=tuple(
            (str(key), str(value))
            for key, value in sorted((item.get("metadata") or {}).items())
        ),
    )


def cognitive_claims(observations: tuple[Observation, ...]) -> tuple[ExtractedClaim, ...]:
    extractor = DocumentClaimExtractor()
    return tuple(
        claim
        for item in observations
        for claim in extractor.extract(
            EnvironmentObservation(
                id=item.id,
                source=item.environment,
                content=item.payload,
            )
        )
    )


def main() -> None:
    url = os.environ.get("CASHFLOW_OBSERVATION_URL", DEFAULT_URL)
    root = Path(os.environ.get("COGNITIA_PERSISTENCE_ROOT", ".ci/persistence"))
    root.mkdir(parents=True, exist_ok=True)
    path = root / "observations.sqlite"

    with SQLiteObservationStore(path) as store:
        # These questions are open-ended. No historical observation IDs are
        # supplied here. Retrieval must discover relevant experience itself.
        before = store.latest_observed_at(environment=ENVIRONMENT)

        since = before
        batches: list[dict] = []
        acquired_ids: set[str] = set()
        while True:
            payload = fetch_environment(url, since=since, limit=BATCH_LIMIT)
            batch = tuple(to_observation(item, url) for item in payload["observations"])
            next_since = payload.get("nextSince")
            batches.append({
                "since": since,
                "observation_count": len(batch),
                "nextSince": next_since,
            })
            for observation in batch:
                try:
                    store.get(observation.id)
                except KeyError:
                    acquired_ids.add(observation.id)
                store.ingest(observation)

            if not batch or len(batch) < BATCH_LIMIT:
                break
            if not isinstance(next_since, str) or not next_since or (since is not None and next_since <= since):
                break
            since = next_since

        retained = store.by_environment(ENVIRONMENT)
        timestamped = sorted(
            retained,
            key=lambda item: (item.observed_at or "", item.id),
        )
        current = tuple(timestamped[-CURRENT_LIMIT:])
        current_ids = {item.id for item in current}

        retriever = ObservationExperienceRetriever()
        current_claims = cognitive_claims(current)
        all_historical = tuple(item for item in timestamped if item.id not in current_ids)
        all_historical_claims = cognitive_claims(all_historical)
        question_results = []

        for question in QUESTIONS:
            matches = retriever.retrieve(
                store,
                question,
                environment=ENVIRONMENT,
                exclude_ids=current_ids,
                limit=12,
            )
            retrieved = tuple(store.get(match.observation_id) for match in matches)
            historical_claims = cognitive_claims(retrieved)

            controller = ResearchActionController()
            blind = controller.choose(
                question,
                claims=current_claims,
                unresolved=("historical context not retrieved",),
            )
            informed = controller.choose(
                question,
                claims=current_claims + historical_claims,
                unresolved=("relationship between historical and current evidence needs checking",),
            )
            ablated = controller.choose(
                question,
                claims=current_claims,
                unresolved=("selected historical experience withheld",),
            )

            question_results.append({
                "question": question,
                "retrieval": {
                    "candidate_count": len(matches),
                    "matches": [
                        {
                            "observation_id": match.observation_id,
                            "score": match.score,
                            "matched_terms": list(match.matched_terms),
                        }
                        for match in matches
                    ],
                },
                "retrieved_claim_count": len(historical_claims),
                "all_historical_claim_count": len(all_historical_claims),
                "current_claim_count": len(current_claims),
                "decisions": {
                    "blind": _decision(blind),
                    "experience_informed": _decision(informed),
                    "history_ablated": _decision(ablated),
                },
                "retrieval_changed_action": bool(
                    blind and informed and blind.action.query.objective != informed.action.query.objective
                ),
                "retrieval_changed_rationale": bool(
                    blind and informed and blind.rationale != informed.rationale
                ),
            })

    artifact = {
        "questions": list(QUESTIONS),
        "open_ended": True,
        "history_supplied_to_experiment": False,
        "acquisition": {
            "initial_since": before,
            "batches": batches,
            "new_observations_acquired": len(acquired_ids),
        },
        "current_observation_count": len(current),
        "question_results": question_results,
    }

    output = Path(".ci/open-ended-experience-retrieval.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")

    assert len(question_results) == len(QUESTIONS)
    for result in question_results:
        assert result["retrieval"]["candidate_count"] > 0, (
            f"open-ended retrieval found no relevant retained experience for: {result['question']}"
        )
        assert result["retrieved_claim_count"] > 0, (
            f"retrieved experience produced no claims for: {result['question']}"
        )
        assert result["decisions"]["experience_informed"] is not None, (
            f"experience-informed controller produced no decision for: {result['question']}"
        )

    print("OPEN_ENDED_EXPERIENCE_RETRIEVAL_SUCCESS")
    for result in question_results:
        print(f"question={result['question']}")
        print(f"retrieved_observations={result['retrieval']['candidate_count']}")
        print(f"retrieved_claims={result['retrieved_claim_count']}")
        print(f"blind_action={result['decisions']['blind']['objective'] if result['decisions']['blind'] else None}")
        print(f"informed_action={result['decisions']['experience_informed']['objective']}")
        print(f"history_ablated_action={result['decisions']['history_ablated']['objective'] if result['decisions']['history_ablated'] else None}")
    print(f"artifact={output}")
def _decision(decision):
    if decision is None:
        return None
    return {
        "objective": decision.action.query.objective,
        "purpose": decision.action.purpose,
        "rationale": decision.rationale,
        "expected_information_gain": decision.expected_information_gain,
    }


if __name__ == "__main__":
    main()
