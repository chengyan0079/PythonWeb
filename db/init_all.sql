-- =============================================
-- PythonWeb 数据库初始化 (DDL + 初始数据)
-- 
-- 使用方式:
--   psql -U postgres -d pythonweb -f db/init_all.sql
-- 
-- 或分步执行:
--   psql -U postgres -d pythonweb -f db/schema.sql
--   psql -U postgres -d pythonweb -f db/init_data.sql
-- =============================================

\echo '============================================'
\echo ' PythonWeb - Database Initialization'
\echo '============================================'

\echo ''
\echo '[1/2] Creating tables...'
\i schema.sql

\echo ''
\echo '[2/2] Inserting initial data...'
\i init_data.sql

\echo ''
\echo '============================================'
\echo ' Database initialization complete!'
\echo '============================================'
