CREATE TABLE application_reviews (
    id BIGINT NOT NULL AUTO_INCREMENT,
    application_id BIGINT NOT NULL,
    reviewer_id BIGINT NOT NULL,
    action_type VARCHAR(40) NOT NULL,
    previous_status VARCHAR(40) NULL,
    new_status VARCHAR(40) NOT NULL,
    internal_note VARCHAR(2000) NULL,
    applicant_message VARCHAR(1000) NULL,
    decision_reason VARCHAR(1000) NULL,
    decision_outcome VARCHAR(32) NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (id),
    KEY idx_application_reviews_application_created (application_id, created_at),
    KEY idx_application_reviews_reviewer (reviewer_id),
    CONSTRAINT fk_application_reviews_application FOREIGN KEY (application_id) REFERENCES credit_applications(id),
    CONSTRAINT fk_application_reviews_reviewer FOREIGN KEY (reviewer_id) REFERENCES users(id)
) ENGINE=InnoDB;

ALTER TABLE credit_applications
    ADD COLUMN review_status VARCHAR(40) NOT NULL DEFAULT 'SUBMITTED';
