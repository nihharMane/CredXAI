package CredXAI.exception;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.HttpRequestMethodNotSupportedException;
import org.springframework.web.servlet.resource.NoResourceFoundException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import tools.jackson.core.JacksonException;
import jakarta.servlet.http.HttpServletRequest;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;
import org.slf4j.MDC;

@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    private ResponseEntity<Map<String, Object>> error(HttpStatus status, String message) {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("timestamp", Instant.now().toString());
        body.put("status", status.value());
        body.put("error", status.getReasonPhrase());
        body.put("message", message);
        String correlationId = MDC.get("correlationId");
        if (correlationId != null) body.put("correlationId", correlationId);
        return ResponseEntity.status(status).body(body);
    }

    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<Map<String, Object>> handleNotFound(ResourceNotFoundException ex) {
        log.warn("Requested resource was not found");
        return error(HttpStatus.NOT_FOUND, ex.getMessage());
    }

    @ExceptionHandler(NoResourceFoundException.class)
    public ResponseEntity<Map<String, Object>> handleUnmappedResource(NoResourceFoundException ex) {
        log.debug("No handler or static resource matched the requested path");
        return error(HttpStatus.NOT_FOUND, "The requested endpoint was not found");
    }

    @ExceptionHandler(MlServiceUnavailableException.class)
    public ResponseEntity<Map<String, Object>> handleMlUnavailable(MlServiceUnavailableException ex) {
        // MlPredictionService logs this expected dependency failure once, without request data.
        return error(HttpStatus.SERVICE_UNAVAILABLE,
                "The prediction service is temporarily unavailable. Please try again later.");
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleValidation(MethodArgumentNotValidException ex) {
        String message = ex.getBindingResult().getFieldErrors().stream()
                .map(e -> e.getField() + ": " + e.getDefaultMessage())
                .findFirst().orElse("Invalid request");
        log.warn("Request validation failed fields={}", ex.getBindingResult().getFieldErrors().stream()
                .map(e -> e.getField().replaceAll("[^A-Za-z0-9_.-]", ""))
                .distinct().toList());
        return error(HttpStatus.BAD_REQUEST, message);
    }

    @ExceptionHandler({HttpMessageNotReadableException.class,
            MissingServletRequestParameterException.class,
            MethodArgumentTypeMismatchException.class})
    public ResponseEntity<Map<String, Object>> handleBadRequest(Exception ex, HttpServletRequest request) {
        if (ex instanceof MissingServletRequestParameterException missing) {
            log.warn("Malformed request received method={} path={} missing_parameter={}",
                    request.getMethod(), request.getRequestURI(), missing.getParameterName());
            return error(HttpStatus.BAD_REQUEST, "A required request parameter is missing.");
        } else if (ex instanceof HttpMessageNotReadableException) {
            String invalidField = findInvalidField(ex);
            if ("bill_payment_consistency_percent".equals(invalidField)) {
                log.warn("Malformed request received method={} path={} field={} reason=invalid_number",
                        request.getMethod(), request.getRequestURI(), invalidField);
                return error(HttpStatus.BAD_REQUEST,
                        "Bill payment consistency must be a number from 0% to 100% with no more than two decimal places.");
            }
            if ("tenure_months".equals(invalidField)) {
                log.warn("Malformed request received method={} path={} field={} reason=invalid_number",
                        request.getMethod(), request.getRequestURI(), invalidField);
                return error(HttpStatus.BAD_REQUEST,
                        "Requested repayment tenure must be a whole number from 1 to 600 months.");
            }
            log.warn("Malformed request received method={} path={} reason=invalid_or_missing_json_body",
                    request.getMethod(), request.getRequestURI());
            return error(HttpStatus.BAD_REQUEST, "The request body is missing or malformed.");
        } else if (ex instanceof MethodArgumentTypeMismatchException mismatch) {
            log.warn("Malformed request received method={} path={} parameter={} reason=invalid_value_type",
                    request.getMethod(), request.getRequestURI(), mismatch.getName());
            return error(HttpStatus.BAD_REQUEST, "A request value has an invalid format.");
        } else {
            log.warn("Malformed request received method={} path={} reason={}",
                    request.getMethod(), request.getRequestURI(), ex.getClass().getSimpleName());
        }
        return error(HttpStatus.BAD_REQUEST, "Invalid or incomplete request");
    }

    private String findInvalidField(Throwable exception) {
        for (Throwable cause = exception; cause != null; cause = cause.getCause()) {
            if (cause instanceof JacksonException jacksonException) {
                for (JacksonException.Reference reference : jacksonException.getPath()) {
                    if ("bill_payment_consistency_percent".equals(reference.getPropertyName())
                            || "tenure_months".equals(reference.getPropertyName())) {
                        return reference.getPropertyName();
                    }
                }
            }
        }
        return null;
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<Map<String, Object>> handleIllegalArgument(IllegalArgumentException ex) {
        log.warn("Request rejected by business validation");
        return error(HttpStatus.BAD_REQUEST, ex.getMessage() == null ? "Invalid request" : ex.getMessage());
    }

    @ExceptionHandler(DataIntegrityViolationException.class)
    public ResponseEntity<Map<String, Object>> handleDatabaseConflict(DataIntegrityViolationException ex) {
        // Do not log the exception message/SQL parameters, which can contain user data.
        log.warn("Database integrity constraint rejected an operation ({})", ex.getClass().getSimpleName());
        return error(HttpStatus.CONFLICT, "The operation conflicts with existing data");
    }

    @ExceptionHandler(HttpRequestMethodNotSupportedException.class)
    public ResponseEntity<Map<String, Object>> handleMethodNotAllowed(HttpRequestMethodNotSupportedException ex) {
        log.warn("Unsupported HTTP method rejected");
        return error(HttpStatus.METHOD_NOT_ALLOWED, "HTTP method not supported for this endpoint");
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handleGeneral(Exception ex) {
        log.error("Unexpected application error ({})", ex.getClass().getSimpleName(), ex);
        return error(HttpStatus.INTERNAL_SERVER_ERROR, "An unexpected error occurred");
    }
}
