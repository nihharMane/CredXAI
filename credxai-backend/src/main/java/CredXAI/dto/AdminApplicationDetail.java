package CredXAI.dto;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record AdminApplicationDetail(Long id, Long applicantId, String applicantName, String applicantEmail,
        String modelType, String predictionStatus, String reviewStatus, Double defaultProbability,
        String riskBand, BigDecimal loanAmount, Integer tenureMonths, BigDecimal existingMonthlyDebt,
        String repaymentHistory, String purpose, String modelVersion, String predictionDetails,
        LocalDateTime createdAt) {}
