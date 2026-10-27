import unittest

from pydantic import ValidationError

from ml_api.alternative_api import AlternativeCreditApplication, _build_model_features


def request(**overrides):
    values = {
        "age_range": "26-35",
        "account_tenure_months": 24,
        "monthly_income": 48000,
        "monthly_spending": 32000,
        "average_balance": 15000,
        "overdraft_frequency_percent": 8.33,
        "bill_payment_consistency_percent": 66.67,
        "cashflow_stability_percent": 85,
    }
    values.update(overrides)
    return AlternativeCreditApplication(**values)


class AlternativePercentageSchemaTests(unittest.TestCase):
    def test_bill_percentage_accepts_zero_hundred_and_two_decimal_values(self):
        self.assertEqual(request(bill_payment_consistency_percent=0).bill_payment_consistency_percent, 0)
        self.assertEqual(request(bill_payment_consistency_percent=100).bill_payment_consistency_percent, 100)
        self.assertEqual(request(bill_payment_consistency_percent=66.67).bill_payment_consistency_percent, 66.67)

    def test_missing_out_of_range_and_non_numeric_bill_values_are_rejected(self):
        for value in (None, -0.01, 100.01, "not-a-number"):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                request(bill_payment_consistency_percent=value)

    def test_percentages_are_scaled_to_the_ratio_used_during_training(self):
        features = _build_model_features(request()).iloc[0]
        self.assertAlmostEqual(features["bill_payment_consistency"], 0.6667)
        self.assertAlmostEqual(features["overdraft_frequency"], 0.0833)
        self.assertAlmostEqual(features["cashflow_stability_score"], 0.85)


if __name__ == "__main__":
    unittest.main()
