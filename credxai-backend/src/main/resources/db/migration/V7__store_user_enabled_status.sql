-- Some existing local schemas already have this column. Add it only when absent.
SET @enabled_column_exists = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'users'
      AND COLUMN_NAME = 'enabled'
);

SET @enabled_column_ddl = IF(
    @enabled_column_exists = 0,
    'ALTER TABLE users ADD COLUMN enabled BOOLEAN NOT NULL DEFAULT TRUE',
    'ALTER TABLE users ALTER COLUMN enabled SET DEFAULT TRUE'
);

PREPARE enabled_column_statement FROM @enabled_column_ddl;
EXECUTE enabled_column_statement;
DEALLOCATE PREPARE enabled_column_statement;
