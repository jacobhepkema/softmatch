import unittest
from softmatch.processing import reverse_complement, find_matches, expand_ambiguous
import regex

class TestAmbiguous(unittest.TestCase):
    def test_reverse_complement_ambiguous(self):
        # Two-option
        self.assertEqual(reverse_complement("R"), "Y")
        self.assertEqual(reverse_complement("Y"), "R")
        self.assertEqual(reverse_complement("K"), "M")
        self.assertEqual(reverse_complement("M"), "K")
        self.assertEqual(reverse_complement("S"), "S")
        self.assertEqual(reverse_complement("W"), "W")

        # Three-option
        self.assertEqual(reverse_complement("B"), "V")
        self.assertEqual(reverse_complement("V"), "B")
        self.assertEqual(reverse_complement("D"), "H")
        self.assertEqual(reverse_complement("H"), "D")

        # Four-option
        self.assertEqual(reverse_complement("N"), "N")

        # Complex sequence
        self.assertEqual(reverse_complement("ATRG"), "CYAT")

    def test_expand_ambiguous(self):
        self.assertEqual(expand_ambiguous("ATR"), "AT[AG]")
        self.assertEqual(expand_ambiguous("YCG"), "[CT]CG")
        self.assertEqual(expand_ambiguous("N"), "[ACGTN]")

    def test_find_matches_ambiguous(self):
        # ATR should match ATG and ATA with 0 errors
        queries = [{'name': 'Ambiguous', 'seq': 'ATR'}]
        # We need to simulate how CLI pre-compiles them
        for q in queries:
            expanded = expand_ambiguous(q['seq'])
            q['fwd_re'] = regex.compile(f"({expanded}){{e<=0}}", regex.BESTMATCH)

        hits = find_matches("ATG", queries, 0)
        self.assertTrue(any(h['match_seq'] == "ATG" and h['errors'] == 0 for h in hits))

        hits = find_matches("ATA", queries, 0)
        self.assertTrue(any(h['match_seq'] == "ATA" and h['errors'] == 0 for h in hits))

        hits = find_matches("ATC", queries, 0)
        self.assertEqual(len(hits), 0)

    def test_find_matches_ambiguous_with_errors(self):
        # ATR with 1 error allowed
        queries = [{'name': 'Ambiguous', 'seq': 'ATR'}]
        for q in queries:
            expanded = expand_ambiguous(q['seq'])
            q['fwd_re'] = regex.compile(f"({expanded}){{e<=1}}", regex.BESTMATCH)

        # AAG matches ATR with 1 error (A vs T)
        hits = find_matches("AAG", queries, 1)
        fwd_hits = [h for h in hits if h['strand'] == 1]
        self.assertEqual(len(fwd_hits), 1)
        self.assertEqual(fwd_hits[0]['errors'], 1)

    def test_reverse_strand_ambiguous(self):
        # Query ATR. RC is YAT ([CT]AT)
        queries = [{'name': 'Ambiguous', 'seq': 'ATR'}]
        for q in queries:
            expanded_fwd = expand_ambiguous(q['seq'])
            q['fwd_re'] = regex.compile(f"({expanded_fwd}){{e<=0}}", regex.BESTMATCH)

            rev_seq = reverse_complement(q['seq'])
            expanded_rev = expand_ambiguous(rev_seq)
            q['rev_re'] = regex.compile(f"({expanded_rev}){{e<=0}}", regex.BESTMATCH)

        # CAT should match reverse strand of ATR
        hits = find_matches("CAT", queries, 0)
        rev_hits = [h for h in hits if h['strand'] == -1]
        self.assertEqual(len(rev_hits), 1)
        self.assertEqual(rev_hits[0]['match_seq'], "CAT")

if __name__ == "__main__":
    unittest.main()
