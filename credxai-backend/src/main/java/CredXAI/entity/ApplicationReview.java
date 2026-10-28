package CredXAI.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "application_reviews")
public class ApplicationReview {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @ManyToOne(optional = false) @JoinColumn(name = "application_id", nullable = false)
    private CreditApplication application;
    @ManyToOne(optional = false) @JoinColumn(name = "reviewer_id", nullable = false)
    private User reviewer;
    @Column(name = "action_type", nullable = false, length = 40)
    private String actionType;
    @Column(name = "previous_status", length = 40)
    private String previousStatus;
    @Column(name = "new_status", nullable = false, length = 40)
    private String newStatus;
    @Column(name = "internal_note", length = 2000)
    private String internalNote;
    @Column(name = "applicant_message", length = 1000)
    private String applicantMessage;
    @Column(name = "decision_reason", length = 1000)
    private String decisionReason;
    @Column(name = "decision_outcome", length = 32)
    private String decisionOutcome;
    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    protected ApplicationReview() {}
    public ApplicationReview(CreditApplication application, User reviewer, String actionType,
                             String previousStatus, String newStatus, String internalNote,
                             String applicantMessage, String decisionReason, String decisionOutcome) {
        this.application = application; this.reviewer = reviewer; this.actionType = actionType;
        this.previousStatus = previousStatus; this.newStatus = newStatus;
        this.internalNote = internalNote; this.applicantMessage = applicantMessage;
        this.decisionReason = decisionReason; this.decisionOutcome = decisionOutcome;
    }
    public Long getId() { return id; }
    public CreditApplication getApplication() { return application; }
    public User getReviewer() { return reviewer; }
    public String getActionType() { return actionType; }
    public String getPreviousStatus() { return previousStatus; }
    public String getNewStatus() { return newStatus; }
    public String getInternalNote() { return internalNote; }
    public String getApplicantMessage() { return applicantMessage; }
    public String getDecisionReason() { return decisionReason; }
    public String getDecisionOutcome() { return decisionOutcome; }
    public LocalDateTime getCreatedAt() { return createdAt; }
}
