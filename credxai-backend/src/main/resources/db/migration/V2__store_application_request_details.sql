ALTER TABLE credit_applications
    ADD COLUMN loan_amount DECIMAL(15,2) NULL,
    ADD COLUMN purpose VARCHAR(120) NULL;
