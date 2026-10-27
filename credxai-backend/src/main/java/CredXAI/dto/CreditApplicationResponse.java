package CredXAI.dto;

import java.time.LocalDateTime;
import java.math.BigDecimal;

public class CreditApplicationResponse {
    public Long id;
    public Long userId;
    public String modelType;
    public String status;
    public Double defaultProbability;
    public String riskBand;
    public BigDecimal loanAmount;
    public BigDecimal existingMonthlyDebt;
    public String repaymentHistory;
    public String purpose;
    public String modelVersion;
    public String predictionDetails;
    public LocalDateTime createdAt;

    public CreditApplicationResponse() {
    }

    public CreditApplicationResponse(Long id, Long userId, String modelType,
                                   String status, Double defaultProbability,
                                   String riskBand, BigDecimal loanAmount, String purpose,
                                   BigDecimal existingMonthlyDebt, String modelVersion,
                                   String predictionDetails, String repaymentHistory, LocalDateTime createdAt) {
        this.id = id;
        this.userId = userId;
        this.modelType = modelType;
        this.status = status;
        this.defaultProbability = defaultProbability;
        this.riskBand = riskBand;
        this.loanAmount = loanAmount;
        this.existingMonthlyDebt = existingMonthlyDebt;
        this.repaymentHistory = repaymentHistory;
        this.purpose = purpose;
        this.modelVersion = modelVersion;
        this.predictionDetails = predictionDetails;
        this.createdAt = createdAt;
    }
}
