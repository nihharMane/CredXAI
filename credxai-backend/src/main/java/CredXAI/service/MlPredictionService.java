package CredXAI.service;

import CredXAI.dto.AlternativePredictionRequest;
import CredXAI.dto.TraditionalPredictionRequest;
import CredXAI.exception.MlServiceUnavailableException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;
import tools.jackson.databind.JsonNode;

import java.util.LinkedHashMap;
import java.util.Map;

@Service
public class MlPredictionService {

    private static final Logger log = LoggerFactory.getLogger(MlPredictionService.class);

    private final RestClient restClient;
    private final String alternativeUrl;
    private final String traditionalUrl;

    public MlPredictionService(
            RestClient.Builder builder,
            @Value("${credxai.ml.alternative-url}") String alternativeUrl,
            @Value("${credxai.ml.traditional-url}") String traditionalUrl) {
        this.restClient = builder.build();
        this.alternativeUrl = alternativeUrl;
        this.traditionalUrl = traditionalUrl;
    }

    public JsonNode predictAlternative(AlternativePredictionRequest request) {
        Map<String, Object> modelInput = new LinkedHashMap<>();
        modelInput.put("age_range", request.age_range);
        modelInput.put("account_tenure_months", request.account_tenure_months);
        modelInput.put("monthly_income", request.monthly_income);
        modelInput.put("monthly_spending", request.monthly_spending);
        modelInput.put("average_balance", request.average_balance);
        modelInput.put("overdraft_frequency_percent", request.overdraft_frequency_percent);
        modelInput.put("bill_payment_consistency_percent", request.bill_payment_consistency_percent);
        modelInput.put("cashflow_stability_percent", request.cashflow_stability_percent);
        // Application context is retained by Spring but is not a model feature.
        return callPredictionService("alternative", alternativeUrl, modelInput);
    }

    public JsonNode predictTraditional(TraditionalPredictionRequest request) {
        Map<String, Object> modelInput = new LinkedHashMap<>();
        modelInput.put("age", request.age);
        modelInput.put("children", request.children);
        modelInput.put("family_members", request.family_members);
        modelInput.put("income_type", request.income_type);
        modelInput.put("monthly_income", request.monthly_income);
        modelInput.put("credit_amount", request.credit_amount);
        modelInput.put("monthly_installment", request.monthly_installment);
        modelInput.put("goods_price", request.goods_price);
        modelInput.put("owns_car", request.owns_car);
        modelInput.put("owns_property", request.owns_property);
        modelInput.put("education", request.education);
        modelInput.put("housing_type", request.housing_type);
        // Purpose, separately reported existing obligations, and repayment-history
        // summary are recorded with the application but are not model features.
        return callPredictionService("traditional", traditionalUrl, modelInput);
    }

    private JsonNode callPredictionService(String model, String baseUrl, Object request) {
        long startedAt = System.nanoTime();
        log.debug("Calling ML prediction service model={}", model);
        try {
            JsonNode result = restClient.post()
                    .uri(baseUrl + "/predict")
                    .body(request)
                    .retrieve()
                    .body(JsonNode.class);

            if (result == null || result.isNull() || !result.isObject()) {
                log.warn("ML service response rejected model={} reason=empty_or_invalid_json", model);
                throw new MlServiceUnavailableException("Invalid response from ML service", null);
            }

            JsonNode probability = result.get("default_probability");
            String expectedModelType = model.equals("alternative")
                    ? "ALTERNATIVE_DATA" : "TRADITIONAL_DATA";
            String riskBand = result.path("risk_band").asString("");
            if (probability == null || !probability.isNumber()
                    || !Double.isFinite(probability.doubleValue())
                    || probability.doubleValue() < 0.0 || probability.doubleValue() > 1.0
                    || !expectedModelType.equals(result.path("model_type").asString())
                    || !java.util.Set.of("LOW_RISK", "MEDIUM_RISK", "HIGH_RISK").contains(riskBand)
                    || result.path("model_version").asString("").isBlank()) {
                log.warn("ML service response rejected model={} reason=invalid_prediction_schema", model);
                throw new MlServiceUnavailableException("Invalid response from ML service", null);
            }

            log.info("ML prediction completed model={} durationMs={}", model,
                    (System.nanoTime() - startedAt) / 1_000_000);
            return result;
        } catch (MlServiceUnavailableException ex) {
            throw ex;
        } catch (RestClientException ex) {
            // Avoid logging request payloads; they may contain financial information.
            log.warn("ML service unavailable model={} exceptionType={} durationMs={}", model,
                    ex.getClass().getSimpleName(), (System.nanoTime() - startedAt) / 1_000_000);
            throw new MlServiceUnavailableException("ML prediction service call failed", ex);
        }
    }
}
