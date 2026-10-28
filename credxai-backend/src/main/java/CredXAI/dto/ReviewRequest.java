package CredXAI.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public record ReviewRequest(
        @NotBlank @Pattern(regexp = "UNDER_REVIEW|ADDITIONAL_INFORMATION_REQUIRED|DECISION_RECORDED") String status,
        @Size(max = 2000) String internalNote,
        @Size(max = 1000) String applicantMessage,
        @Size(max = 1000) String decisionReason,
        @Pattern(regexp = "|APPROVE|DECLINE|REQUEST_REASSESSMENT|OTHER") String decisionOutcome) {}
