import unittest

from models import Claim, Verdict
from service import apply_accepted_replacements


class RevisionTests(unittest.TestCase):
    def test_only_explicitly_accepted_replacements_are_applied(self):
        scene = "The event happened in 1987. Anna sent a text message."
        date_claim = Claim(id="C1", text="Wrong date", script_quote="1987", start_offset=22, end_offset=26, category="HISTORY", question="Date?", search_queries=["event date"])
        text_claim = Claim(id="C2", text="Wrong technology", script_quote="text message", start_offset=40, end_offset=52, category="TECHNOLOGY", question="SMS?", search_queries=["first SMS"])
        verdicts = [
            Verdict(claim=date_claim, status="INACCURATE", confidence=100, finding="Wrong", replacement_text="1989", sources=[]),
            Verdict(claim=text_claim, status="INACCURATE", confidence=100, finding="Wrong", replacement_text="landline call", sources=[]),
        ]
        revised = apply_accepted_replacements(scene, verdicts, {"C1"})
        self.assertEqual(revised, "The event happened in 1989. Anna sent a text message.")

    def test_invalid_offsets_never_modify_the_scene(self):
        scene = "Original screenplay text"
        claim = Claim(id="C1", text="Claim", script_quote="missing", start_offset=None, end_offset=None, category="OTHER", question="Question?", search_queries=["query words"])
        verdict = Verdict(claim=claim, status="INACCURATE", confidence=80, finding="Finding", replacement_text="replacement", sources=[])
        self.assertEqual(apply_accepted_replacements(scene, [verdict], {"C1"}), scene)


if __name__ == "__main__":
    unittest.main()
