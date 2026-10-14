
package CredXAI.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

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

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
}
