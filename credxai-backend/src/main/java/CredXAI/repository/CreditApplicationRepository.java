
package CredXAI.repository;

import CredXAI.entity.CreditApplication;
import CredXAI.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface CreditApplicationRepository
        extends JpaRepository<CreditApplication, Long> {

    List<CreditApplication> findByUser(User user);

    List<CreditApplication> findByUserId(Long userId);
}
