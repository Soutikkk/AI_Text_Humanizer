"""
Unit tests for checking Heuristic Humanizer Logic
"""

import unittest
from humanizer import (
    humanize_text,
    replace_repetitive_words,
    improve_sentence_flow,
    get_synonyms
)


class TestAIHumanizer(unittest.TestCase):

    def test_empty_input(self):
        """Verifies that empty, None, and whitespace-only strings are handled gracefully."""
        self.assertEqual(humanize_text(""), "")
        self.assertEqual(humanize_text("   "), "")
        self.assertEqual(humanize_text(None), "")

    def test_synonym_lookup(self):
        """Verifies that synonym retrieval returns valid results."""
        syns = get_synonyms("important")
        self.assertTrue(len(syns) > 0)
        self.assertNotIn("important", syns)

    def test_replace_repetitive_words(self):
        """Verifies that repeated occurrences of words are replaced with synonyms."""
        # 'important' repeated multiple times should trigger replacement
        text = "This is important. It is important to remember that it is an important topic."
        result = replace_repetitive_words(text)
        self.assertNotEqual(text, result)
        # The first instance of 'important' should stay, but later ones can be replaced
        self.assertIn("important", result)
        
    def test_improve_sentence_flow_robotic(self):
        """Verifies that robotic phrases are replaced with natural alternatives."""
        text = "In order to succeed, we must utilize our time. Furthermore, we must not quit."
        result = improve_sentence_flow(text, strength="High")
        # 'utilize' should be replaced by 'use' or 'employ'
        self.assertNotIn("utilize", result.lower())
        self.assertNotIn("in order to", result.lower())

    def test_improve_sentence_flow_contractions(self):
        """Verifies that formal terms are contracted under Medium and High strength."""
        text = "It is not possible to do that because we do not have time."
        
        # Low strength should NOT contract
        low_result = improve_sentence_flow(text, strength="Low")
        self.assertIn("do not", low_result)
        self.assertIn("is not", low_result)

        # Medium strength should contract
        med_result = improve_sentence_flow(text, strength="Medium")
        self.assertNotIn("do not", med_result)
        self.assertNotIn("is not", med_result)

    def test_improve_sentence_flow_splitting(self):
        """Verifies that long compound sentences are broken down into shorter ones."""
        long_sentence = (
            "We wanted to visit the local library because they had a lot of historical records, "
            "and we also wanted to see the ancient manuscripts which are preserved there in special rooms."
        )
        result = improve_sentence_flow(long_sentence, strength="Medium")
        # Sentence splitting should occur, breaking at ', and'
        self.assertIn(".", result)
        self.assertNotIn(", and", result)


if __name__ == "__main__":
    unittest.main()
