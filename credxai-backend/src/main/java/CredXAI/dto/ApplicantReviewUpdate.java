package CredXAI.dto;

import java.time.LocalDateTime;

public record ApplicantReviewUpdate(String status, String message, String decisionReason, LocalDateTime updatedAt) {}
