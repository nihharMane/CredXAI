package CredXAI;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfSystemProperty;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
@EnabledIfSystemProperty(named = "credxai.integration", matches = "true")
class CredxaiBackendApplicationTests {

    @Test
    void contextLoadsWithConfiguredLocalDependencies() {
    }
}
