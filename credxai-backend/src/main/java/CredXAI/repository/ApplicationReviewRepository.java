package CredXAI.repository;

import CredXAI.entity.ApplicationReview;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface ApplicationReviewRepository extends JpaRepository<ApplicationReview, Long> {
    List<ApplicationReview> findByApplicationIdOrderByCreatedAtDesc(Long applicationId);
    List<ApplicationReview> findByApplicationIdAndApplicantMessageIsNotNullOrderByCreatedAtDesc(Long applicationId);
}
