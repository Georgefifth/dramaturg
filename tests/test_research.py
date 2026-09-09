import unittest

from models import Source
from service import CoverageResult, merge_sources, research_targets


class ResearchPlanningTests(unittest.TestCase):
    def test_only_two_claims_can_trigger_second_pass(self):
        audits = [
            CoverageResult(claim_id=f"C{index}", status="NEEDS_MORE", rationale="Missing primary evidence", refined_queries=[f"query {index}"])
            for index in range(1, 5)
        ]
        self.assertEqual([item.claim_id for item in research_targets(audits)], ["C1", "C2"])

    def test_sufficient_claim_does_not_trigger_second_pass(self):
        audits = [
            CoverageResult(claim_id="C1", status="SUFFICIENT", rationale="Sources agree", refined_queries=[]),
            CoverageResult(claim_id="C2", status="NEEDS_MORE", rationale="Need an archive", refined_queries=["official archive date"]),
        ]
        self.assertEqual([item.claim_id for item in research_targets(audits)], ["C2"])

    def test_second_pass_sources_are_deduplicated_and_reindexed(self):
        initial = [
            Source(id="S1", title="A", url="https://example.com/a", excerpt="A"),
            Source(id="S2", title="B", url="https://example.com/b", excerpt="B"),
        ]
        follow_up = [
            Source(id="S1", title="Duplicate", url="https://example.com/a", excerpt="Duplicate"),
            Source(id="S2", title="C", url="https://example.com/c", excerpt="C"),
        ]
        merged = merge_sources(initial, follow_up)
        self.assertEqual([source.url for source in merged], ["https://example.com/a", "https://example.com/b", "https://example.com/c"])
        self.assertEqual([source.id for source in merged], ["S1", "S2", "S3"])


if __name__ == "__main__":
    unittest.main()
