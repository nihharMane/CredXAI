
package CredXAI.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Digits;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

import java.math.BigDecimal;

public class TraditionalPredictionRequest {
    @Min(18)
    @Max(100)
    public int age;
    @Min(0)
    @Max(20)
    public int children;
    @Min(1)
    @Max(20)
    public int family_members;
    @NotBlank
    @Size(max = 80)
    public String income_type;
    @NotNull
    @DecimalMin("0.01")
    @DecimalMax("1000000000")
    public double monthly_income;
    @NotNull
    @DecimalMin("0.01")
    @DecimalMax("9999999999999.99")
    @Digits(integer = 13, fraction = 2)
    public BigDecimal credit_amount;
    @NotNull
    @DecimalMin("0")
    @DecimalMax("9999999999999.99")
    @Digits(integer = 13, fraction = 2)
    public BigDecimal existing_monthly_debt;
    @NotBlank
    @Pattern(regexp = "UNKNOWN|CURRENT|LATE_1_30|LATE_31_90|LATE_OVER_90")
    public String repayment_history;
    @NotBlank
    @Size(max = 120)
    public String purpose;
    @DecimalMin("0.01")
    @DecimalMax("1000000000")
    public double monthly_installment;
    @DecimalMin("0.01")
    @DecimalMax("1000000000")
    public double goods_price;
    @NotBlank
    @Pattern(regexp = "Y|N")
    public String owns_car;
    @NotBlank
    @Pattern(regexp = "Y|N")
    public String owns_property;
    @NotBlank
    @Size(max = 80)
    public String education;
    @NotBlank
    @Size(max = 80)
    public String housing_type;
}
