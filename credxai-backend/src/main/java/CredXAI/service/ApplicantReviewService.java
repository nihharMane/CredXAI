package CredXAI.service;

import CredXAI.dto.ApplicantReviewUpdate;
import CredXAI.exception.ResourceNotFoundException;
import CredXAI.repository.ApplicationReviewRepository;
import CredXAI.repository.CreditApplicationRepository;
import CredXAI.repository.UserRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;

@Service
public class ApplicantReviewService {
    private final CreditApplicationRepository applications;
    private final ApplicationReviewRepository reviews;
    private final UserRepository users;
    public ApplicantReviewService(CreditApplicationRepository applications, ApplicationReviewRepository reviews, UserRepository users) {
        this.applications = applications; this.reviews = reviews; this.users = users;
    }
    @Transactional(readOnly = true)
    public List<ApplicantReviewUpdate> updates(String email, Long applicationId) {
        var user = users.findByEmail(email).orElseThrow(() -> new ResourceNotFoundException("User not found"));
        applications.findByIdAndUserId(applicationId, user.getId()).orElseThrow(() -> new ResourceNotFoundException("Application not found"));
        return reviews.findByApplicationIdAndApplicantMessageIsNotNullOrderByCreatedAtDesc(applicationId).stream()
                .map(row -> new ApplicantReviewUpdate(row.getNewStatus(), row.getApplicantMessage(), row.getDecisionReason(), row.getCreatedAt())).toList();
    }
}
