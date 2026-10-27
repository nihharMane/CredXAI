
package CredXAI.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.math.BigDecimal;

@Entity
@Table(name = "credit_applications")
public class CreditApplication {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(optional = false)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(nullable = false)
    private String modelType;

    @Column(nullable = false)
    private String status = "PENDING";

    private Double defaultProbability;

    private String riskBand;

    @Column(precision = 15, scale = 2)
    private BigDecimal loanAmount;

    @Column(precision = 15, scale = 2)
    private BigDecimal existingMonthlyDebt;

    @Column(length = 32)
    private String repaymentHistory;

    @Column(length = 120)
    private String purpose;

    @Column(length = 80)
    private String modelVersion;

    @Column(columnDefinition = "TEXT")
    private String predictionDetails;

    private LocalDateTime createdAt = LocalDateTime.now();

    public CreditApplication() {
    }

    public Long getId() {
        return id;
    }

    public User getUser() {
        return user;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public String getModelType() {
        return modelType;
    }

    public void setModelType(String modelType) {
        this.modelType = modelType;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Double getDefaultProbability() {
        return defaultProbability;
    }

    public void setDefaultProbability(Double defaultProbability) {
        this.defaultProbability = defaultProbability;
    }

    public String getRiskBand() {
        return riskBand;
    }

    public void setRiskBand(String riskBand) {
        this.riskBand = riskBand;
    }

    public BigDecimal getLoanAmount() { return loanAmount; }

    public void setLoanAmount(BigDecimal loanAmount) { this.loanAmount = loanAmount; }

    public BigDecimal getExistingMonthlyDebt() { return existingMonthlyDebt; }

    public void setExistingMonthlyDebt(BigDecimal existingMonthlyDebt) { this.existingMonthlyDebt = existingMonthlyDebt; }

    public String getRepaymentHistory() { return repaymentHistory; }

    public void setRepaymentHistory(String repaymentHistory) { this.repaymentHistory = repaymentHistory; }

    public String getPurpose() { return purpose; }

    public void setPurpose(String purpose) { this.purpose = purpose; }

    public String getModelVersion() { return modelVersion; }

    public void setModelVersion(String modelVersion) { this.modelVersion = modelVersion; }

    public String getPredictionDetails() { return predictionDetails; }

    public void setPredictionDetails(String predictionDetails) { this.predictionDetails = predictionDetails; }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
}
