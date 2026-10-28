package CredXAI.service;

import CredXAI.dto.AdminApplicationSummary;
import CredXAI.dto.AdminApplicationDetail;
import CredXAI.dto.AdminReviewEntry;
import CredXAI.dto.ReviewRequest;
import CredXAI.entity.ApplicationReview;
import CredXAI.entity.CreditApplication;
import CredXAI.exception.ResourceNotFoundException;
import CredXAI.repository.ApplicationReviewRepository;
import CredXAI.repository.CreditApplicationRepository;
import CredXAI.repository.UserRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.Map;
import java.util.List;

@Service
public class AdminService {
    private final CreditApplicationRepository applications;
    private final ApplicationReviewRepository reviews;
    private final UserRepository users;

    public AdminService(CreditApplicationRepository applications, ApplicationReviewRepository reviews, UserRepository users) {
        this.applications = applications; this.reviews = reviews; this.users = users;
    }

    @Transactional(readOnly = true)
    public Map<String, Object> dashboard() {
        return Map.of("total", applications.count(),
                "submitted", applications.countByReviewStatus("SUBMITTED"),
                "underReview", applications.countByReviewStatus("UNDER_REVIEW"),
                "additionalInformationRequired", applications.countByReviewStatus("ADDITIONAL_INFORMATION_REQUIRED"),
                "decisionRecorded", applications.countByReviewStatus("DECISION_RECORDED"),
                "risk", Map.of("high", applications.countByRiskBand("HIGH_RISK"),
                        "medium", applications.countByRiskBand("MEDIUM_RISK"),
                        "low", applications.countByRiskBand("LOW_RISK")));
    }

    @Transactional(readOnly = true)
    public Page<AdminApplicationSummary> list(String query, String status, String risk, int page, int size, String sort) {
        String safeSort = List.of("createdAt", "id", "loanAmount", "defaultProbability", "reviewStatus").contains(sort) ? sort : "createdAt";
        var pageable = PageRequest.of(Math.max(0, page), Math.max(1, Math.min(size, 100)), Sort.by(Sort.Direction.DESC, safeSort));
        Specification<CreditApplication> spec = (root, cq, cb) -> cb.conjunction();
        if (status != null && !status.isBlank()) spec = spec.and((root, cq, cb) -> cb.equal(root.get("reviewStatus"), status));
        if (risk != null && !risk.isBlank()) spec = spec.and((root, cq, cb) -> cb.equal(root.get("riskBand"), risk));
        if (query != null && !query.isBlank()) {
            String term = query.trim().toLowerCase();
            spec = spec.and((root, cq, cb) -> {
                var applicant = root.join("user");
                var matches = cb.or(cb.like(cb.lower(applicant.get("fullName")), "%" + term + "%"),
                        cb.like(cb.lower(applicant.get("email")), "%" + term + "%"),
                        cb.like(cb.lower(root.get("purpose")), "%" + term + "%"));
                try { matches = cb.or(matches, cb.equal(root.get("id"), Long.valueOf(term.replaceFirst("^#", "")))); }
                catch (NumberFormatException ignored) { }
                return matches;
            });
        }
        return applications.findAll(spec, pageable).map(this::summary);
    }

    @Transactional(readOnly = true)
    public AdminApplicationDetail detail(Long id) {
        var app = find(id);
        return new AdminApplicationDetail(app.getId(), app.getUser().getId(), app.getUser().getFullName(), app.getUser().getEmail(),
                app.getModelType(), app.getStatus(), app.getReviewStatus(), app.getDefaultProbability(), app.getRiskBand(),
                app.getLoanAmount(), app.getTenureMonths(), app.getExistingMonthlyDebt(), app.getRepaymentHistory(), app.getPurpose(),
                app.getModelVersion(), app.getPredictionDetails(), app.getCreatedAt());
    }

    @Transactional(readOnly = true)
    public List<AdminReviewEntry> reviewHistory(Long id) {
        find(id);
        return reviews.findByApplicationIdOrderByCreatedAtDesc(id).stream().map(this::reviewEntry).toList();
    }

    @Transactional
    public AdminReviewEntry addReview(Long id, String reviewerEmail, ReviewRequest request) {
        CreditApplication application = find(id);
        var reviewer = users.findByEmail(reviewerEmail).orElseThrow(() -> new ResourceNotFoundException("Reviewer not found"));
        String next = request.status();
        if ("DECISION_RECORDED".equals(next) && (request.decisionReason() == null || request.decisionReason().isBlank()
                || request.decisionOutcome() == null || request.decisionOutcome().isBlank()))
            throw new IllegalArgumentException("A human decision outcome and reason are required when recording a decision.");
        if ("ADDITIONAL_INFORMATION_REQUIRED".equals(next) && (request.applicantMessage() == null || request.applicantMessage().isBlank()))
            throw new IllegalArgumentException("Add a message describing the information requested from the applicant.");
        String previous = application.getReviewStatus();
        if ("DECISION_RECORDED".equals(previous)) throw new IllegalArgumentException("A recorded decision is final.");
        boolean validTransition = switch (previous) {
            case "SUBMITTED" -> "UNDER_REVIEW".equals(next) || "ADDITIONAL_INFORMATION_REQUIRED".equals(next);
            case "UNDER_REVIEW" -> "ADDITIONAL_INFORMATION_REQUIRED".equals(next) || "DECISION_RECORDED".equals(next);
            case "ADDITIONAL_INFORMATION_REQUIRED" -> "UNDER_REVIEW".equals(next);
            default -> false;
        };
        if (!validTransition) throw new IllegalArgumentException("Choose a valid review status transition.");
        application.setReviewStatus(next);
        ApplicationReview saved = reviews.save(new ApplicationReview(application, reviewer, "STATUS_CHANGE", previous, next,
                clean(request.internalNote()), clean(request.applicantMessage()), clean(request.decisionReason()), clean(request.decisionOutcome())));
        return reviewEntry(saved);
    }

    private CreditApplication find(Long id) { return applications.findById(id).orElseThrow(() -> new ResourceNotFoundException("Application not found")); }
    private AdminApplicationSummary summary(CreditApplication app) {
        return new AdminApplicationSummary(app.getId(), app.getUser().getId(), app.getUser().getFullName(), app.getUser().getEmail(),
                app.getModelType(), app.getStatus(), app.getReviewStatus(), app.getDefaultProbability(), app.getRiskBand(),
                app.getLoanAmount(), app.getPurpose(), app.getCreatedAt());
    }
    private AdminReviewEntry reviewEntry(ApplicationReview row) {
        return new AdminReviewEntry(row.getId(), row.getActionType(), row.getPreviousStatus(), row.getNewStatus(),
                row.getReviewer().getFullName(), row.getInternalNote(), row.getApplicantMessage(), row.getDecisionOutcome(), row.getDecisionReason(), row.getCreatedAt());
    }
    private String clean(String value) { return value == null || value.isBlank() ? null : value.trim(); }
}
