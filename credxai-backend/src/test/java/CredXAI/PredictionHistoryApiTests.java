package CredXAI;

import CredXAI.controller.PredictionController;
import CredXAI.dto.CreditApplicationResponse;
import CredXAI.entity.User;
import CredXAI.exception.ResourceNotFoundException;
import CredXAI.repository.CreditApplicationRepository;
import CredXAI.repository.UserRepository;
import CredXAI.service.CreditApplicationService;
import CredXAI.service.MlPredictionService;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.servlet.resource.NoResourceFoundException;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import CredXAI.exception.GlobalExceptionHandler;
import java.util.List;
import java.util.Optional;
import java.lang.reflect.Proxy;

import static org.junit.jupiter.api.Assertions.*;

class PredictionHistoryApiTests {
    private static final String OWNER = "owner@example.com";

    @Test
    void historyReturnsOnlyRecordsForAuthenticatedIdentity() {
        HistoryService service = new HistoryService();
        PredictionController controller = new PredictionController(null, service);
        var authentication = new UsernamePasswordAuthenticationToken(OWNER, null, List.of());

        List<CreditApplicationResponse> history = controller.getHistory(authentication);

        assertEquals(OWNER, service.requestedUser);
        assertEquals(List.of(13L), history.stream().map(record -> record.id).toList());
    }

    @Test
    void historyCanBeEmpty() {
        HistoryService service = new HistoryService();
        service.records = List.of();
        PredictionController controller = new PredictionController(null, service);

        assertTrue(controller.getHistory(new UsernamePasswordAuthenticationToken(OWNER, null, List.of())).isEmpty());
    }

    @Test
    void detailPassesAuthenticatedIdentityAndRequestedIdToUserScopedService() {
        HistoryService service = new HistoryService();
        PredictionController controller = new PredictionController(null, service);

        var result = controller.getApplication(
                new UsernamePasswordAuthenticationToken(OWNER, null, List.of()), 13L);

        assertEquals(OWNER, service.requestedUser);
        assertEquals(13L, service.requestedId);
        assertEquals(13L, result.id);
        assertHistoryDetailRouteUsesApplicationId();
    }

    @Test
    void detailDoesNotReturnAnotherUsersApplication() {
        User owner = new User();
        owner.setEmail(OWNER);
        try {
            var id = User.class.getDeclaredField("id");
            id.setAccessible(true);
            id.set(owner, 7L);
        } catch (ReflectiveOperationException e) {
            throw new AssertionError(e);
        }
        var userRepository = proxy(UserRepository.class, (method, args) ->
                method.equals("findByEmail") ? Optional.of(owner) : defaultValue(method));
        var applicationRepository = proxy(CreditApplicationRepository.class, (method, args) -> {
            if (method.equals("findByIdAndUserId")) {
                assertEquals(13L, args[0]);
                assertEquals(7L, args[1]);
                return Optional.empty();
            }
            return defaultValue(method);
        });
        CreditApplicationService service = new CreditApplicationService(applicationRepository, userRepository);

        assertThrows(ResourceNotFoundException.class, () -> service.getUserApplication(OWNER, 13L));
    }

    @Test
    void missingRouteReturnsSafeNotFoundAndInvalidPathValueReturnsBadRequest() throws Exception {
        GlobalExceptionHandler handler = new GlobalExceptionHandler();
        var missing = handler.handleUnmappedResource(new NoResourceFoundException(
                HttpMethod.GET, "/api/predictions/unknown", "/api/predictions/unknown"));
        assertEquals(HttpStatus.NOT_FOUND, missing.getStatusCode());
        assertFalse(missing.getBody().toString().contains("NoResourceFoundException"));

        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/api/predictions/history/not-a-number");
        var invalid = handler.handleBadRequest(
                new MethodArgumentTypeMismatchException("not-a-number", Long.class, "applicationId", null, null), request);
        assertEquals(HttpStatus.BAD_REQUEST, invalid.getStatusCode());
        assertFalse(invalid.getBody().toString().contains("not-a-number"));
    }

    private static void assertHistoryDetailRouteUsesApplicationId() {
        var method = java.util.Arrays.stream(PredictionController.class.getDeclaredMethods())
                .filter(candidate -> candidate.getName().equals("getApplication"))
                .findFirst().orElseThrow();
        assertTrue(java.util.Arrays.asList(method.getAnnotation(GetMapping.class).value()).contains("/history/{applicationId}"));
        assertTrue(java.util.Arrays.stream(method.getParameters()).anyMatch(parameter ->
                parameter.isAnnotationPresent(PathVariable.class) && parameter.getType().equals(Long.class)));
    }

    @SuppressWarnings("unchecked")
    private static <T> T proxy(Class<T> type, RepositoryCall call) {
        return (T) Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[]{type},
                (instance, method, args) -> call.invoke(method.getName(), args));
    }

    private static Object defaultValue(String method) {
        return null;
    }

    @FunctionalInterface
    private interface RepositoryCall {
        Object invoke(String method, Object[] args);
    }

    private static final class HistoryService extends CreditApplicationService {
        private String requestedUser;
        private Long requestedId;
        private List<CreditApplicationResponse> records = List.of(new CreditApplicationResponse(
                13L, 1L, "TRADITIONAL_DATA", "COMPLETED", .2, "LOW_RISK", null,
                "PERSONAL", null, "v1", null, "UNKNOWN", null));

        private HistoryService() { super(null, null); }

        @Override public List<CreditApplicationResponse> getUserApplications(String userEmail) {
            requestedUser = userEmail;
            return records;
        }

        @Override public CreditApplicationResponse getUserApplication(String userEmail, Long applicationId) {
            requestedUser = userEmail;
            requestedId = applicationId;
            return records.stream().filter(record -> record.id.equals(applicationId)).findFirst().orElseThrow();
        }
    }
}
