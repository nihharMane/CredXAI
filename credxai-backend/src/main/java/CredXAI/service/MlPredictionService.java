
package CredXAI.service;

import CredXAI.dto.AlternativePredictionRequest;
import CredXAI.dto.TraditionalPredictionRequest;
import tools.jackson.databind.JsonNode;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

@Service
public class MlPredictionService {

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

    public JsonNode predictAlternative(
            AlternativePredictionRequest request) {

        return restClient.post()
                .uri(alternativeUrl + "/predict")
                .body(request)
                .retrieve()
                .body(JsonNode.class);
    }

    public JsonNode predictTraditional(
            TraditionalPredictionRequest request) {

        return restClient.post()
                .uri(traditionalUrl + "/predict")
                .body(request)
                .retrieve()
                .body(JsonNode.class);
    }
}
