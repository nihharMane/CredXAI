# CredXAI Data Schema

## Features

1. upiTransactionFrequency
   - Number of UPI transactions in the last 3 months
   - Type: Integer

2. upiTransactionRegularity
   - Standard deviation of gaps between UPI transactions
   - Type: Decimal

3. utilityPaymentOnTimeRate
   - Proportion of utility bills paid on time
   - Range: 0.0 - 1.0

4. mobileRechargeConsistency
   - Measure of consistency in mobile recharge behavior
   - Type: Decimal

5. debtToIncomeRatio
   - Existing debt divided by income
   - Type: Decimal

6. stabilityMonths
   - Months at current address/employment
   - Type: Integer

7. averageMonthlyInflow
   - Average monthly account inflow
   - Type: Decimal

The dataset used by CredXAI is synthetically generated for research and demonstration purposes. It does not represent real customer or banking data. The synthetic data generation process introduces controlled relationships between alternative-data features and the target default variable to enable model training and evaluation.
