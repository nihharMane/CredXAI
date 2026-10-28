package CredXAI.controller;

import CredXAI.dto.AlternativePredictionRequest;
import CredXAI.dto.TraditionalPredictionRequest;
import CredXAI.service.CreditApplicationService;
import CredXAI.service.MlPredictionService;
import org.springframework.web.bind.annotation.*;
import jakarta.validation.Valid;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.node.ObjectNode;

import java.math.BigDecimal;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@RestController
@RequestMapping("/api/predictions")
public class PredictionController {

    private static final Logger log = LoggerFactory.getLogger(PredictionController.class);

    private final MlPredictionService mlPredictionService;
    private final CreditApplicationService applicationService;

    public PredictionController(
            MlPredictionService mlPredictionService,
            CreditApplicationService applicationService) {
        this.mlPredictionService = mlPredictionService;
        this.applicationService = applicationService;
    }

    @PostMapping("/alternative")
    public JsonNode predictAlternative(
            org.springframework.security.core.Authentication authentication,
            @Valid @RequestBody AlternativePredictionRequest request) {

        long startedAt = System.nanoTime();
        log.debug("Alternative assessment request accepted");
        JsonNode prediction =
                mlPredictionService.predictAlternative(request);
        if (prediction instanceof ObjectNode objectPrediction) objectPrediction.put("tenure_months", request.tenure_months);

        var application = applicationService.savePrediction(
                authentication.getName(), prediction, request.loan_amount, request.existing_monthly_debt,
                request.repayment_history, request.purpose);
        log.info("Assessment persisted applicationId={} model=alternative durationMs={}", application.getId(),
                (System.nanoTime() - startedAt) / 1_000_000);
        return withApplicationMetadata(prediction, application.getId(), application.getLoanAmount(), application.getExistingMonthlyDebt(),
                application.getPurpose(), application.getRepaymentHistory(), application.getStatus(),
                application.getCreatedAt().toString(), application.getModelVersion(), application.getTenureMonths());
    }

    @PostMapping("/traditional")
    public JsonNode predictTraditional(
            org.springframework.security.core.Authentication authentication,
            @Valid @RequestBody TraditionalPredictionRequest request) {

        long startedAt = System.nanoTime();
        log.debug("Traditional assessment request accepted");
        JsonNode prediction =
                mlPredictionService.predictTraditional(request);
        if (prediction instanceof ObjectNode objectPrediction) objectPrediction.put("tenure_months", request.tenure_months);

        var application = applicationService.savePrediction(
                authentication.getName(), prediction, request.credit_amount, request.existing_monthly_debt,
                request.repayment_history, request.purpose);
        log.info("Assessment persisted applicationId={} model=traditional durationMs={}", application.getId(),
                (System.nanoTime() - startedAt) / 1_000_000);
        return withApplicationMetadata(prediction, application.getId(), application.getLoanAmount(), application.getExistingMonthlyDebt(),
                application.getPurpose(), application.getRepaymentHistory(), application.getStatus(),
                application.getCreatedAt().toString(), application.getModelVersion(), application.getTenureMonths());
    }

    @GetMapping("/history")
    public java.util.List<CredXAI.dto.CreditApplicationResponse> getHistory(
            org.springframework.security.core.Authentication authentication) {
        String userEmail = authentication.getName();
        var applications = applicationService.getUserApplications(userEmail);
        log.debug("Application history loaded count={}", applications.size());
        return applications;
    }

    @GetMapping("/history/{applicationId}")
    public CredXAI.dto.CreditApplicationResponse getApplication(
            org.springframework.security.core.Authentication authentication,
            @PathVariable Long applicationId) {
        var application = applicationService.getUserApplication(authentication.getName(), applicationId);
        log.debug("Application assessment loaded applicationId={}", applicationId);
        return application;
    }

    private JsonNode withApplicationMetadata(JsonNode prediction, Long applicationId,
                                             BigDecimal loanAmount, BigDecimal existingMonthlyDebt,
                                             String purpose, String repaymentHistory, String applicationStatus, String timestamp,
                                             String modelVersion, Integer tenureMonths) {
        ObjectNode response = ((ObjectNode) prediction).deepCopy();
        response.put("application_id", applicationId);
        response.put("requested_loan_amount", loanAmount);
        if (tenureMonths != null) response.put("tenure_months", tenureMonths);
        response.put("existing_monthly_debt", existingMonthlyDebt);
        response.put("repayment_history", repaymentHistory);
        response.put("application_status", applicationStatus);
        response.put("purpose", purpose);
        response.put("assessment_timestamp", timestamp);
        response.put("model_version", modelVersion);
        return response;
    }
}
