package CredXAI.dto;

import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Digits;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

import java.math.BigDecimal;

/** Alternative behavioral-data inputs plus persisted application context. */
public class AlternativePredictionRequest {
    @NotBlank
    public String age_range;
    @NotNull @DecimalMin("0") @DecimalMax("600") @Digits(integer = 3, fraction = 0)
    public BigDecimal account_tenure_months;
    @NotNull @DecimalMin(value = "0.01") @Digits(integer = 13, fraction = 2)
    public BigDecimal monthly_income;
    @NotNull @DecimalMin("0") @Digits(integer = 13, fraction = 2)
    public BigDecimal monthly_spending;
    @NotNull @Digits(integer = 13, fraction = 2)
    public BigDecimal average_balance;
    @NotNull(message = "Overdraft frequency is required.")
    @DecimalMin(value = "0", message = "Overdraft frequency must be between 0% and 100%.")
    @DecimalMax(value = "100", message = "Overdraft frequency must be between 0% and 100%.")
    @Digits(integer = 3, fraction = 2, message = "Overdraft frequency must have no more than two decimal places.")
    public BigDecimal overdraft_frequency_percent;
    @NotNull(message = "Bill payment consistency is required.")
    @DecimalMin(value = "0", message = "Bill payment consistency must be between 0% and 100%.")
    @DecimalMax(value = "100", message = "Bill payment consistency must be between 0% and 100%.")
    @Digits(integer = 3, fraction = 2, message = "Bill payment consistency must have no more than two decimal places.")
    public BigDecimal bill_payment_consistency_percent;
    @NotNull @DecimalMin("0") @DecimalMax("100") @Digits(integer = 3, fraction = 2)
    public BigDecimal cashflow_stability_percent;

    // Application context retained for persistence; these values are not model inputs.
    @NotNull @DecimalMin("0.01") @DecimalMax("9999999999999.99") @Digits(integer = 13, fraction = 2)
    public BigDecimal loan_amount;
    @NotNull @DecimalMin("0") @DecimalMax("9999999999999.99") @Digits(integer = 13, fraction = 2)
    public BigDecimal existing_monthly_debt;
    @NotBlank @Pattern(regexp = "UNKNOWN|CURRENT|LATE_1_30|LATE_31_90|LATE_OVER_90")
    public String repayment_history;
    @NotBlank @Size(max = 120)
    public String purpose;
}
