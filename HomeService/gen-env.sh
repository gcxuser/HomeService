#!/bin/bash
# .env generator script for HomeService
# Usage: ./gen-env.sh

set -e

ENV_FILE=".env"

echo "Generating .env file for HomeService..."
echo ""

# Generate a secure random key
generate_secret() {
    python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || \
    openssl rand -base64 32 2>/dev/null || \
    echo "your-secure-token-min-32-chars"
}

# Check if .env already exists
if [ -f "$ENV_FILE" ]; then
    read -p ".env file already exists. Overwrite? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Generate the .env file
cat > "$ENV_FILE" << EOF
# HomeService Environment Configuration
# Generated on $(date)

# ============================================
# Database Configuration
# ============================================
DATABASE_URL="sqlite:///./homeservice.db"
# PostgreSQL: "postgresql+psycopg2://homeservice:homeservice@localhost:5432/homeservice"

# ============================================
# API Security
# ============================================
API_SECRET_KEY="${API_SECRET_KEY:-$(generate_secret)}"
ADMIN_USERNAME="${ADMIN_USERNAME:-admin}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-password123}"

# ============================================
# LLM Provider Configuration
# ============================================
LLM_PROVIDER="${LLM_PROVIDER:-claude}"
LLM_API_KEY="${LLM_API_KEY:-}"
LLM_BASE_URL="${LLM_BASE_URL:-https://api.anthropic.com/v1/}"
LLM_MODEL_NAME="${LLM_MODEL_NAME:-claude-3-5-sonnet-20241022}"

# ============================================
# RAG Configuration
# ============================================
EMBEDDING_MODEL="${EMBEDDING_MODEL:-text-embedding-3-small}"
VECTOR_DIMENSION="${VECTOR_DIMENSION:-1536}"
ENABLE_CACHE="${ENABLE_CACHE:-true}"

# ============================================
# Debug & Logging
# ============================================
DEBUG="${DEBUG:-false}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"
LOG_FORMAT="${LOG_FORMAT:-json}"

# ============================================
# Business Configuration
# ============================================
DEFAULT_SERVICE_DURATION="${DEFAULT_SERVICE_DURATION:-120}"
MAX_APPOINTMENTS_PER_DAY="${MAX_APPOINTMENTS_PER_DAY:-8}"
EOF

echo "✅ .env file generated successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env and set your API keys (LLM_API_KEY, etc.)"
echo "2. Run: pip install -r requirements.txt"
echo "3. Run: uvicorn HomeService.app:app --reload"
echo ""
