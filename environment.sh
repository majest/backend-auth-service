#!/usr/bin/env bash

export APP_ENV=DEV
export APP_NAME=experiment-service
export APP_DEBUG=1
export APP_REDIS_URL=redis://localhost:6379/0
export APP_STATSD_HOST=127.0.0.1
export APP_STATSD_PORT=8125
export APP_STATSD_PREFIX=ea.service.experiment
export APP_DATABASE_URL=postgresql://hal
export APP_LOG_LEVEL=INFO
export STATSD_HOST=localhost
export SECURITY_SIGN_KEY=pE3y/V3eivQQ+AqO628+fD3KtqTd9Z4b
export OAUTH2_PROVIDER_TOKEN_EXPIRES_IN=3600