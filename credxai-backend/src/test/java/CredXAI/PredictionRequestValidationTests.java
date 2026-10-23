package CredXAI;

import CredXAI.dto.AlternativePredictionRequest;
import CredXAI.dto.TraditionalPredictionRequest;
import CredXAI.controller.PredictionController;
import CredXAI.exception.GlobalExceptionHandler;
import jakarta.validation.Validation;
import jakarta.validation.Validator;
import org.junit.jupiter.api.Test;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.mock.http.MockHttpInputMessage;
import tools.jackson.core.JacksonException;
import tools.jackson.databind.json.JsonMapper;

import java.math.BigDecimal;
import java.util.Set;
import java.lang.reflect.Method;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class PredictionRequestValidationTests {

    private final Validator validator = Validation.buildDefaultValidatorFactory().getValidator();

    @Test
    void alternativeRequestEnforcesBehavioralFeatureAndContextBounds() {
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

        assertTrue(validator.validate(request).isEmpty());

        request.bill_payment_consistency_percent = new BigDecimal("101");
        request.loan_amount = BigDecimal.ZERO;
        request.repayment_history = "UNSUPPORTED";
        Set<String> invalidFields = validator.validate(request).stream()
                .map(error -> error.getPropertyPath().toString())
                .collect(Collectors.toSet());

        assertTrue(invalidFields.contains("bill_payment_consistency_percent"));
        assertTrue(invalidFields.contains("loan_amount"));
        assertTrue(invalidFields.contains("repayment_history"));
    }

    @Test
    void billPaymentPercentageAcceptsTrainingCompatibleBoundariesAndPrecision() {
        AlternativePredictionRequest request = new AlternativePredictionRequest();

        for (String value : new String[]{"0", "100", "66.67"}) {
            request.bill_payment_consistency_percent = new BigDecimal(value);
            assertFalse(fieldViolations(request, "bill_payment_consistency_percent").size() > 0,
                    "Expected valid percentage " + value);
        }
    }

    @Test
    void overdraftPercentageUsesTheSamePercentageRange() {
        AlternativePredictionRequest request = new AlternativePredictionRequest();
        for (String value : new String[]{"0", "100", "8.33"}) {
            request.overdraft_frequency_percent = new BigDecimal(value);
            assertTrue(fieldViolations(request, "overdraft_frequency_percent").isEmpty(),
                    "Expected valid percentage " + value);
        }
        request.overdraft_frequency_percent = new BigDecimal("100.01");
        assertFieldMessage(request, "overdraft_frequency_percent", "Overdraft frequency must be between 0% and 100%.");
    }

    @Test
    void billPaymentPercentageRejectsMissingOutOfRangeAndExcessPrecisionWithFieldMessage() {
        AlternativePredictionRequest request = new AlternativePredictionRequest();
        request.bill_payment_consistency_percent = null;
        assertFieldMessage(request, "bill_payment_consistency_percent", "Bill payment consistency is required.");

        for (String value : new String[]{"-0.01", "100.01", "66.666"}) {
            request.bill_payment_consistency_percent = new BigDecimal(value);
            assertTrue(fieldViolations(request, "bill_payment_consistency_percent").size() > 0,
                    "Expected invalid percentage " + value);
        }
        request.bill_payment_consistency_percent = new BigDecimal("100.01");
        assertFieldMessage(request, "bill_payment_consistency_percent", "Bill payment consistency must be between 0% and 100%.");
        request.bill_payment_consistency_percent = new BigDecimal("66.666");
        assertFieldMessage(request, "bill_payment_consistency_percent", "Bill payment consistency must have no more than two decimal places.");
    }

    @Test
    void nonNumericBillPaymentValueReturnsFieldSpecificSafeMessage() throws Exception {
        JsonMapper mapper = JsonMapper.builder().build();
        HttpMessageNotReadableException malformed;
        try {
            mapper.readValue("{\"bill_payment_consistency_percent\":\"not-a-number\"}", AlternativePredictionRequest.class);
            throw new AssertionError("Expected malformed numeric input to be rejected");
        } catch (JacksonException ex) {
            malformed = new HttpMessageNotReadableException("Malformed request body", ex,
                    new MockHttpInputMessage(new byte[0]));
        }

        MockHttpServletRequest request = new MockHttpServletRequest("POST", "/api/predictions/alternative");
        var response = new GlobalExceptionHandler().handleBadRequest(malformed, request);
        assertTrue(response.getStatusCode().isSameCodeAs(HttpStatus.BAD_REQUEST));
        assertTrue(response.getBody().get("message").toString().contains("Bill payment consistency"));
        assertFalse(response.getBody().toString().contains("not-a-number"));
    }

    @Test
    void emptyBillPaymentValueIsReportedOnItsField() throws Exception {
        JsonMapper mapper = JsonMapper.builder().build();
        MockHttpServletRequest servletRequest = new MockHttpServletRequest("POST", "/api/predictions/alternative");
        try {
            AlternativePredictionRequest request = mapper.readValue(
                    "{\"bill_payment_consistency_percent\":\"\"}", AlternativePredictionRequest.class);
            assertFieldMessage(request, "bill_payment_consistency_percent", "Bill payment consistency is required.");
        } catch (JacksonException ex) {
            var malformed = new HttpMessageNotReadableException("Malformed request body", ex,
                    new MockHttpInputMessage(new byte[0]));
            var response = new GlobalExceptionHandler().handleBadRequest(malformed, servletRequest);
            assertTrue(response.getStatusCode().isSameCodeAs(HttpStatus.BAD_REQUEST));
            assertTrue(response.getBody().get("message").toString().contains("Bill payment consistency"));
        }
    }

    private Set<jakarta.validation.ConstraintViolation<AlternativePredictionRequest>> fieldViolations(
            AlternativePredictionRequest request, String field) {
        return validator.validate(request).stream()
                .filter(violation -> violation.getPropertyPath().toString().equals(field))
                .collect(Collectors.toSet());
    }

    private void assertFieldMessage(AlternativePredictionRequest request, String field, String expectedMessage) {
        assertTrue(fieldViolations(request, field).stream()
                .anyMatch(violation -> violation.getMessage().equals(expectedMessage)));
    }

    @Test
    void traditionalRequestEnforcesPositiveAmountAndSupportedOwnershipFlags() {
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

        assertTrue(validator.validate(request).isEmpty());

        request.credit_amount = BigDecimal.ZERO;
        request.owns_car = "UNKNOWN";
        Set<String> invalidFields = validator.validate(request).stream()
                .map(error -> error.getPropertyPath().toString())
                .collect(Collectors.toSet());

        assertTrue(invalidFields.contains("credit_amount"));
        assertTrue(invalidFields.contains("owns_car"));
        assertFalse(invalidFields.isEmpty());

        request.credit_amount = null;
        assertTrue(validator.validate(request).stream()
                .anyMatch(error -> error.getPropertyPath().toString().equals("credit_amount")));
    }

    @Test
    void predictionEndpointsUseJsonBodiesAndDoNotRequireServletParameters() throws Exception {
        assertJsonBodyEndpoint("predictTraditional", "/traditional", TraditionalPredictionRequest.class);
        assertJsonBodyEndpoint("predictAlternative", "/alternative", AlternativePredictionRequest.class);
    }

    @Test
    void missingServletParameterReturnsSafeClientError() {
        MockHttpServletRequest request = new MockHttpServletRequest("POST", "/api/predictions/traditional");
        var response = new GlobalExceptionHandler().handleBadRequest(
                new MissingServletRequestParameterException("requiredValue", "String"), request);

        assertTrue(response.getStatusCode().isSameCodeAs(HttpStatus.BAD_REQUEST));
        assertTrue(response.getBody().get("message").toString().contains("required request parameter"));
        assertFalse(response.getBody().toString().contains("requiredValue"));
    }

    private void assertJsonBodyEndpoint(String methodName, String route, Class<?> requestType) throws Exception {
        Method method = java.util.Arrays.stream(PredictionController.class.getDeclaredMethods())
                .filter(candidate -> candidate.getName().equals(methodName))
                .findFirst().orElseThrow();
        assertTrue(method.isAnnotationPresent(PostMapping.class));
        assertTrue(java.util.Arrays.asList(method.getAnnotation(PostMapping.class).value()).contains(route));
        assertTrue(java.util.Arrays.stream(method.getParameters())
                .anyMatch(parameter -> parameter.isAnnotationPresent(RequestBody.class)
                        && parameter.getType().equals(requestType)));
        assertFalse(java.util.Arrays.stream(method.getParameters())
                .anyMatch(parameter -> parameter.isAnnotationPresent(RequestParam.class)));
    }
}
