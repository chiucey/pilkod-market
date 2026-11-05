<<{auth_service, blocks, token_validator}.
<<{auth_service, blocks, rate_limiter}.
<<{token_validator, blocks, user_db}.
<<{rate_limiter, blocks, redis_cache}.
<<{user_db, blocks, audit_log}.
<<{redis_cache, blocks, audit_log}.
<<{audit_log, blocks, deploy}.
