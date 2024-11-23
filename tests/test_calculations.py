import unittest
from src.processing_pytorch import calculate_credits_pytorch, calculate_credits_batch_pytorch
from src.processing_pandas import calculate_credits_pandas, calculate_credits_batch_pandas


class TestCalculateCredits(unittest.TestCase):
    def test_base_cost(self):
        # max(Base cost + char cost - bonus, 1) * word multiplier
        self.assertEqual(calculate_credits_pytorch(["-"])[0], 2)
        self.assertEqual(calculate_credits_pandas(["-"])[0], 2)

    def test_character_count_and_word_length_multipliers(self):
        # Base cost 1 + char cost 0.85 + word cost 0.6 + vowels 0.6 - bonus 2
        self.assertAlmostEqual(calculate_credits_pytorch(["What is the rent?"])[0], 1.05, places=4)
        self.assertAlmostEqual(calculate_credits_pandas(["What is the rent?"])[0], 1.05, places=4)

        # Base cost 1 + char cost 1 + word cost 0.7 + vowels 0.9
        self.assertAlmostEqual(calculate_credits_pytorch(["What is is the rent?"])[0], 3.6, places=4)
        self.assertAlmostEqual(calculate_credits_pandas(["What is is the rent?"])[0], 3.6, places=4)

    def test_third_vowels(self):
        # Base cost 1 + char cost 0.75 + word cost 0.5 + vowels 1.5
        self.assertAlmostEqual(calculate_credits_pytorch(["--a -i -a -a -a"])[0], 3.75, places=4)
        self.assertAlmostEqual(calculate_credits_pandas(["--a -i -a -a -a"])[0], 3.75, places=4)

        # Base cost 1 + char cost 0.75 + word cost 0.5 + vowels 0
        self.assertEqual(calculate_credits_pytorch(["-a- i- a- a- a-"])[0], 2.25)
        self.assertEqual(calculate_credits_pandas(["-a- i- a- a- a-"])[0], 2.25)

    def test_length_penalty(self):
        # (Base cost 1 + char cost 5.05 + word cost 0.3 + vowels 0 + length penalty 5 - bonus 2) * 2
        long_text = ("z" * 100) + '-'
        self.assertAlmostEqual(calculate_credits_pytorch([long_text])[0], 18.7, places=4)
        self.assertAlmostEqual(calculate_credits_pandas([long_text])[0], 18.7, places=4)

    def test_palindrome_doubling(self):
        # max(Base cost 1 + char cost 0.1 + word cost 0.1 + vowels 0 - bonus 2, 1)
        self.assertEqual(calculate_credits_pytorch(["az"])[0], 1)
        self.assertEqual(calculate_credits_pandas(["az"])[0], 1)

        # max(Base cost 1 + char cost 0.1 + word cost 0.1 + vowels 0 - bonus 2, 1) * 2
        self.assertEqual(calculate_credits_pytorch(["a"])[0], 2)
        self.assertEqual(calculate_credits_pandas(["a"])[0], 2)

    def test_batch_processing(self):
        # Test batch processing for both PyTorch and Pandas
        messages = [
            "-",
            "What is the rent?",
            "--a -i -a -a -a",
            "z" * 100 + "-",
            "az"
        ]
        expected_results = [2, 1.05, 3.75, 18.7, 1]
        results = calculate_credits_batch_pytorch(messages, batch_size=2)
        print(results)
        for expected, actual in zip(expected_results, results):
            self.assertAlmostEqual(expected, actual, places=4, msg=f"Expected {expected_results}, got {results}")

        results = calculate_credits_batch_pandas(messages, batch_size=2)
        for expected, actual in zip(expected_results, results):
            self.assertAlmostEqual(expected, actual, places=4, msg=f"Expected {expected_results}, got {results}")

        results = calculate_credits_batch_pytorch(messages, batch_size=10)
        for expected, actual in zip(expected_results, results):
            self.assertAlmostEqual(expected, actual, places=4, msg=f"Expected {expected_results}, got {results}")

        results = calculate_credits_batch_pandas(messages, batch_size=10)
        for expected, actual in zip(expected_results, results):
            self.assertAlmostEqual(expected, actual, places=4, msg=f"Expected {expected_results}, got {results}")
