package CredXAI.service;

import CredXAI.dto.CreditApplicationResponse;
import CredXAI.entity.CreditApplication;
import CredXAI.entity.User;
import CredXAI.exception.ResourceNotFoundException;
import CredXAI.repository.CreditApplicationRepository;
import CredXAI.repository.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import tools.jackson.databind.JsonNode;

import java.util.List;
import java.math.BigDecimal;

@Service
public class CreditApplicationService {

    private static final Logger log = LoggerFactory.getLogger(CreditApplicationService.class);

    private final CreditApplicationRepository applicationRepository;
    private final UserRepository userRepository;

    public CreditApplicationService(CreditApplicationRepository applicationRepository,
                                    UserRepository userRepository) {
        this.applicationRepository = applicationRepository;
        this.userRepository = userRepository;
    }

    @Transactional
    public CreditApplication savePrediction(String userEmail, JsonNode prediction, BigDecimal loanAmount,
                                            BigDecimal existingMonthlyDebt, String repaymentHistory, String purpose) {
        User user = userRepository.findByEmail(userEmail)
                .orElseThrow(() -> new ResourceNotFoundException("User not found"));

        CreditApplication application = new CreditApplication();
        application.setUser(user);
        application.setModelType(prediction.path("model_type").asString());
        application.setDefaultProbability(prediction.path("default_probability").asDouble());
        application.setRiskBand(prediction.path("risk_band").asString());
        application.setLoanAmount(loanAmount);
        application.setExistingMonthlyDebt(existingMonthlyDebt);
        application.setRepaymentHistory(repaymentHistory);
        application.setPurpose(purpose.trim());
        application.setModelVersion(prediction.path("model_version").asString("unversioned"));
        application.setPredictionDetails(prediction.toString());
        application.setStatus("COMPLETED");

        CreditApplication saved = applicationRepository.save(application);
        log.info("Credit application persisted applicationId={} model={} status={}", saved.getId(),
                saved.getModelType(), saved.getStatus());
        return saved;
    }

    @Transactional(readOnly = true)
    public List<CreditApplicationResponse> getUserApplications(String userEmail) {
        User user = userRepository.findByEmail(userEmail)
                .orElseThrow(() -> new ResourceNotFoundException("User not found"));

        List<CreditApplicationResponse> applications = applicationRepository.findByUserIdOrderByCreatedAtDesc(user.getId())
                .stream()
                .map(app -> new CreditApplicationResponse(
                        app.getId(), app.getUser().getId(), app.getModelType(), app.getStatus(),
                        app.getDefaultProbability(), app.getRiskBand(), app.getLoanAmount(), app.getPurpose(),
                        app.getExistingMonthlyDebt(), app.getModelVersion(), null, app.getRepaymentHistory(), app.getCreatedAt()))
                .toList();
        log.debug("Application history loaded count={}", applications.size());
        return applications;
    }

    @Transactional(readOnly = true)
    public CreditApplicationResponse getUserApplication(String userEmail, Long applicationId) {
        User user = userRepository.findByEmail(userEmail)
                .orElseThrow(() -> new ResourceNotFoundException("User not found"));

        CreditApplication application = applicationRepository.findByIdAndUserId(applicationId, user.getId())
                .orElseThrow(() -> new ResourceNotFoundException("Application not found"));

        log.debug("Application detail authorized applicationId={}", application.getId());

        return new CreditApplicationResponse(application.getId(), application.getUser().getId(),
                application.getModelType(), application.getStatus(), application.getDefaultProbability(),
                application.getRiskBand(), application.getLoanAmount(), application.getPurpose(),
                application.getExistingMonthlyDebt(), application.getModelVersion(),
                application.getPredictionDetails(), application.getRepaymentHistory(), application.getCreatedAt());
    }
}
