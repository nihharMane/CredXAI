package CredXAI.controller;

import CredXAI.dto.ApplicantReviewUpdate;
import CredXAI.service.ApplicantReviewService;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/predictions/history/{applicationId}/reviews")
public class ApplicantReviewController {
    private final ApplicantReviewService service;
    public ApplicantReviewController(ApplicantReviewService service) { this.service = service; }
    @GetMapping
    public List<ApplicantReviewUpdate> updates(Authentication auth, @PathVariable Long applicationId) {
        return service.updates(auth.getName(), applicationId);
    }
}
