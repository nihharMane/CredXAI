package CredXAI.service;

import CredXAI.dto.AuthResponse;
import CredXAI.dto.LoginRequest;
import CredXAI.dto.RegisterRequest;
import CredXAI.entity.User;
import CredXAI.repository.UserRepository;
import CredXAI.security.JwtUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthService {

    private static final Logger log = LoggerFactory.getLogger(AuthService.class);

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    public AuthService(UserRepository userRepository, PasswordEncoder passwordEncoder, JwtUtil jwtUtil) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtUtil = jwtUtil;
    }

    public AuthResponse register(RegisterRequest request) {
        if (request.fullName == null || request.fullName.isBlank()
                || request.email == null || request.email.isBlank()
                || request.password == null || request.password.length() < 8) {
            throw new IllegalArgumentException(
                    "Name and email are required; password must be at least 8 characters.");
        }

        String email = request.email.trim().toLowerCase();
        if (userRepository.existsByEmail(email)) {
            throw new IllegalArgumentException("Email is already registered.");
        }

        User user = new User();
        user.setFullName(request.fullName.trim());
        user.setEmail(email);
        user.setPassword(passwordEncoder.encode(request.password));
        user.setRole("USER");
        user.setEnabled(true);
        User saved = userRepository.save(user);

        log.info("Applicant registration completed");
        return new AuthResponse(saved.getId(), saved.getFullName(), saved.getEmail(), saved.getRole(), null);
    }

    public AuthResponse login(LoginRequest request) {
        String email = request.email == null ? "" : request.email.trim().toLowerCase();
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new IllegalArgumentException("Invalid email or password."));

        if (request.password == null || !passwordEncoder.matches(request.password, user.getPassword())) {
            throw new IllegalArgumentException("Invalid email or password.");
        }

        String token = jwtUtil.generateToken(user.getEmail(), user.getRole());
        log.info("Applicant authentication completed");
        return new AuthResponse(user.getId(), user.getFullName(), user.getEmail(), user.getRole(), token);
    }
}
