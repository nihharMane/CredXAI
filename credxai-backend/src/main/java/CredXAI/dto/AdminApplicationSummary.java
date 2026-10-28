package CredXAI.dto;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record AdminApplicationSummary(Long id, Long applicantId, String applicantName, String applicantEmail,
                                      String modelType, String predictionStatus, String reviewStatus, Double defaultProbability,
                                      String riskBand, BigDecimal loanAmount, String purpose,
                                      LocalDateTime createdAt) {}
