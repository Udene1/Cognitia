from pathlib import Path
import traceback


def main() -> None:
    output = []
    try:
        from cognitia.answering import AnsweringCore
        from cognitia.research_synthesis import FactorExplanation, ResearchSynthesis

        factors = tuple(
            FactorExplanation(
                factor=factor,
                contribution=contribution,
                claim_ids=(f"c{i}",),
                source_count=1,
                origin_count=1,
                confidence="candidate",
                domain=domain,
            )
            for i, (factor, contribution, domain) in enumerate(
                (
                    ("political instability and civil conflict weakened governance", "Political instability weakened the Roman Empire through repeated civil conflict.", "political"),
                    ("frontier pressure weakened armed forces", "Frontier pressure contributed by weakening armed forces.", "military"),
                    ("fiscal strain reduced reliable tax revenue", "Fiscal strain contributed because tax revenue became less reliable.", "economic"),
                ),
                1,
            )
        )
        synthesis = ResearchSynthesis(
            question="Why did the Roman Empire decline?",
            status="candidate_multi_factor_synthesis",
            thesis="candidate synthesis",
            factors=factors,
            complementary_domains=("political", "military", "economic"),
            competing_explanations=(),
            distinguishing_evidence=("independent verification", "mechanism and timing check"),
            caveats=("Finding count is not independent-source count.",),
            next_actions=("Acquire independent evidence.", "Test the mechanism."),
        )
        answer = AnsweringCore().build(synthesis)
        output.extend(
            (
                f"sufficient={answer.sufficient}",
                f"assessment={answer.assessment}",
                f"answer={answer.answer}",
                f"reasoning={answer.reasoning}",
                f"evidence={answer.evidence}",
                f"uncertainty={answer.uncertainty}",
                f"epistemic={answer.epistemic}",
            )
        )
    except Exception:
        output.append(traceback.format_exc())
    path = Path(".ci/answering-diagnostics.txt")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(output), encoding="utf-8")
    print("\n".join(output))


if __name__ == "__main__":
    main()
