package CredXAI.controller;

import CredXAI.dto.ReviewRequest;
import CredXAI.service.AdminService;
import jakarta.validation.Valid;
import org.springframework.data.domain.Page;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/api/admin")
public class AdminController {
    private final AdminService service;
    public AdminController(AdminService service) { this.service = service; }

    @GetMapping("/dashboard")
    public Map<String, Object> dashboard() { return service.dashboard(); }

    @GetMapping("/applications")
    public Page<?> applications(@RequestParam(required = false) String q,
            @RequestParam(required = false) String status, @RequestParam(required = false) String risk,
            @RequestParam(defaultValue = "0") int page, @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "createdAt") String sort) {
        return service.list(q, status, risk, page, size, sort);
    }

    @GetMapping("/applications/{id}")
    public Object detail(@PathVariable Long id) { return service.detail(id); }

    @GetMapping("/applications/{id}/reviews")
    public Object reviews(@PathVariable Long id) { return service.reviewHistory(id); }

    @PostMapping("/applications/{id}/reviews")
    public Object review(@PathVariable Long id, org.springframework.security.core.Authentication auth,
                        @Valid @RequestBody ReviewRequest request) {
        return service.addReview(id, auth.getName(), request);
    }
}
