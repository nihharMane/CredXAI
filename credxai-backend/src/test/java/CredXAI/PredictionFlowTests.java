package CredXAI;

import CredXAI.controller.PredictionController;
import CredXAI.dto.AlternativePredictionRequest;
import CredXAI.dto.TraditionalPredictionRequest;
import CredXAI.entity.CreditApplication;
import CredXAI.exception.MlServiceUnavailableException;
import CredXAI.service.CreditApplicationService;
import CredXAI.service.MlPredictionService;
import org.junit.jupiter.api.Test;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.web.client.RestClient;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class PredictionFlowTests {
    private static final String EMAIL = "applicant@example.com";
    private static final UsernamePasswordAuthenticationToken AUTH =
            new UsernamePasswordAuthenticationToken(EMAIL, null, List.of());

    @Test
    void traditionalPredictionUsesTraditionalMlAndPersistsForAuthenticatedUser() throws Exception {
        JsonNode prediction = prediction("TRADITIONAL_DATA");
        StubMlService ml = new StubMlService(prediction, false);
        CapturingApplications applications = new CapturingApplications();
        PredictionController controller = new PredictionController(ml, applications);
        TraditionalPredictionRequest request = validTraditionalRequest();

        JsonNode response = controller.predictTraditional(AUTH, request);

        assertEquals("traditional", ml.selectedPipeline);
        assertEquals("applicant@example.com", applications.userEmail);
        assertEquals(request.credit_amount, applications.loanAmount);
        assertEquals("TRADITIONAL_DATA", response.path("model_type").asString());
        assertEquals(81L, response.path("application_id").asLong());
        assertEquals("sha256:saved-version", response.path("model_version").asString());
        assertEquals(0.25, response.path("default_probability").asDouble());
        assertTrue(response.path("risk_increasing_factors").isArray());
        assertTrue(response.path("explanation").isArray());
    }

    @Test
    void alternativePredictionUsesAlternativeMlAndPersistsForAuthenticatedUser() throws Exception {
        JsonNode prediction = prediction("ALTERNATIVE_DATA");
        StubMlService ml = new StubMlService(prediction, false);
        CapturingApplications applications = new CapturingApplications();
        PredictionController controller = new PredictionController(ml, applications);
        AlternativePredictionRequest request = validAlternativeRequest();

        JsonNode response = controller.predictAlternative(AUTH, request);

        assertEquals("alternative", ml.selectedPipeline);
        assertEquals("applicant@example.com", applications.userEmail);
        assertEquals(request.loan_amount, applications.loanAmount);
        assertEquals("ALTERNATIVE_DATA", response.path("model_type").asString());
        assertEquals(81L, response.path("application_id").asLong());
        assertEquals("sha256:saved-version", response.path("model_version").asString());
        assertEquals(0.25, response.path("default_probability").asDouble());
        assertTrue(response.path("risk_reducing_factors").isArray());
    }

    @Test
    void failedTraditionalMlCallDoesNotPersistAnApplication() {
        StubMlService ml = new StubMlService(null, true);
        CapturingApplications applications = new CapturingApplications();
        PredictionController controller = new PredictionController(ml, applications);

        assertThrows(MlServiceUnavailableException.class,
                () -> controller.predictTraditional(AUTH, validTraditionalRequest()));
        assertNull(applications.userEmail);
    }

    private static JsonNode prediction(String modelType) throws Exception {
        return JsonMapper.builder().build().readTree("""
                {"model_type":"%s","prediction":0,"default_probability":0.25,
                 "default_probability_percent":25.0,"risk_band":"LOW_RISK",
                 "risk_increasing_factors":[],"risk_reducing_factors":[],
                 "explanation":["test explanation"],"model_version":"sha256:ml-version"}
                """.formatted(modelType));
    }

    private static TraditionalPredictionRequest validTraditionalRequest() {
        TraditionalPredictionRequest request = new TraditionalPredictionRequest();
        request.age = 35;
        request.children = 0;
        request.family_members = 2;
        request.income_type = "Working";
        request.monthly_income = 45_000;
        request.credit_amount = new BigDecimal("250000.00");
        request.existing_monthly_debt = BigDecimal.ZERO;
        request.repayment_history = "UNKNOWN";
        request.purpose = "PERSONAL";
        request.monthly_installment = 12_500;
        request.goods_price = 240_000;
        request.owns_car = "Y";
        request.owns_property = "Y";
        request.education = "Higher education";
        request.housing_type = "House / apartment";
        return request;
    }

    private static AlternativePredictionRequest validAlternativeRequest() {
        AlternativePredictionRequest request = new AlternativePredictionRequest();
        request.age_range = "26-35";
        request.account_tenure_months = new BigDecimal("24");
        request.monthly_income = new BigDecimal("48000");
        request.monthly_spending = new BigDecimal("32000");
        request.average_balance = new BigDecimal("15000");
        request.overdraft_frequency_percent = new BigDecimal("5");
        request.bill_payment_consistency_percent = new BigDecimal("95");
        request.cashflow_stability_percent = new BigDecimal("85");
        request.loan_amount = new BigDecimal("250000.00");
        request.existing_monthly_debt = BigDecimal.ZERO;
        request.repayment_history = "UNKNOWN";
        request.purpose = "PERSONAL";
        return request;
    }

    private static final class StubMlService extends MlPredictionService {
        private final JsonNode prediction;
        private final boolean fail;
        private String selectedPipeline;

        private StubMlService(JsonNode prediction, boolean fail) {
            super(RestClient.builder().requestFactory(new SimpleClientHttpRequestFactory()),
                    "http://unused-alternative", "http://unused-traditional");
            this.prediction = prediction;
            this.fail = fail;
        }

        @Override
        public JsonNode predictTraditional(TraditionalPredictionRequest request) {
            selectedPipeline = "traditional";
            if (fail) throw new MlServiceUnavailableException("test failure", null);
            return prediction;
        }

        @Override
        public JsonNode predictAlternative(AlternativePredictionRequest request) {
            selectedPipeline = "alternative";
            if (fail) throw new MlServiceUnavailableException("test failure", null);
            return prediction;
        }
    }

    private static final class CapturingApplications extends CreditApplicationService {
        private String userEmail;
        private BigDecimal loanAmount;

        private CapturingApplications() {
            super(null, null);
        }

        @Override
        public CreditApplication savePrediction(String userEmail, JsonNode prediction, BigDecimal loanAmount,
                                                BigDecimal existingMonthlyDebt, String repaymentHistory, String purpose) {
            this.userEmail = userEmail;
            this.loanAmount = loanAmount;
            return new SavedApplication(prediction.path("model_type").asString(), loanAmount,
                    existingMonthlyDebt, repaymentHistory, purpose);
        }
    }

    private static final class SavedApplication extends CreditApplication {
        private final String modelType;
        private final BigDecimal loanAmount;
        private final BigDecimal existingMonthlyDebt;
        private final String repaymentHistory;
        private final String purpose;

        private SavedApplication(String modelType, BigDecimal loanAmount, BigDecimal existingMonthlyDebt,
                                 String repaymentHistory, String purpose) {
            this.modelType = modelType;
            this.loanAmount = loanAmount;
            this.existingMonthlyDebt = existingMonthlyDebt;
            this.repaymentHistory = repaymentHistory;
            this.purpose = purpose;
        }

        @Override public Long getId() { return 81L; }
        @Override public String getModelType() { return modelType; }
        @Override public BigDecimal getLoanAmount() { return loanAmount; }
        @Override public BigDecimal getExistingMonthlyDebt() { return existingMonthlyDebt; }
        @Override public String getRepaymentHistory() { return repaymentHistory; }
        @Override public String getPurpose() { return purpose; }
        @Override public String getStatus() { return "COMPLETED"; }
        @Override public String getModelVersion() { return "sha256:saved-version"; }
        @Override public LocalDateTime getCreatedAt() { return LocalDateTime.parse("2026-10-22T10:00:00"); }
    }
}
