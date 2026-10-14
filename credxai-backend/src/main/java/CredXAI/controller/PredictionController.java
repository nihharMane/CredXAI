
package CredXAI.controller;

import CredXAI.dto.AlternativePredictionRequest;
import CredXAI.dto.TraditionalPredictionRequest;
import CredXAI.service.MlPredictionService;
import tools.jackson.databind.JsonNode;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/predictions")
public class PredictionController {

    private final MlPredictionService mlPredictionService;

    public PredictionController(MlPredictionService mlPredictionService) {
        this.mlPredictionService = mlPredictionService;
    }

    @PostMapping("/alternative")
    public JsonNode predictAlternative(
            @RequestBody AlternativePredictionRequest request) {
        return mlPredictionService.predictAlternative(request);
    }

    @PostMapping("/traditional")
    public JsonNode predictTraditional(
            @RequestBody TraditionalPredictionRequest request) {
        return mlPredictionService.predictTraditional(request);
    }
}
