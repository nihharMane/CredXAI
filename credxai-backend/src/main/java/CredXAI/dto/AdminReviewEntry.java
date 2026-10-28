package CredXAI.dto;

import java.time.LocalDateTime;

public record AdminReviewEntry(Long id, String actionType, String previousStatus, String newStatus,
                               String reviewerName, String internalNote, String applicantMessage,
                               String decisionOutcome, String decisionReason, LocalDateTime createdAt) {}
