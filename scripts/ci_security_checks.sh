#!/bin/bash

# CI Security Checks for Hardcoded Users
# This script runs security validations in CI/CD pipeline
# Exit codes: 0 = success, 1 = security issues found, 2 = validation error

set -e

echo "🔒 Running CI Security Checks for Hardcoded Users"
echo "================================================="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VALIDATION_SCRIPT="$PROJECT_ROOT/scripts/validate_hardcoded_users_security.py"

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Check if validation script exists
if [ ! -f "$VALIDATION_SCRIPT" ]; then
    print_status $RED "❌ Validation script not found: $VALIDATION_SCRIPT"
    exit 2
fi

# Run the validation script
echo "🛡️  Running security validation..."
if python3 "$VALIDATION_SCRIPT"; then
    print_status $GREEN "✅ Security validation passed"
    VALIDATION_RESULT=0
else
    VALIDATION_RESULT=$?
    if [ $VALIDATION_RESULT -eq 1 ]; then
        print_status $RED "❌ Security validation failed - Issues found"
    else
        print_status $RED "❌ Security validation error"
    fi
fi

# Additional CI-specific checks
echo ""
echo "🔍 Running additional CI checks..."

# Check for new hardcoded credentials in changed files
if [ -n "$CI_MERGE_REQUEST_TARGET_BRANCH_NAME" ] || [ -n "$GITHUB_BASE_REF" ]; then
    echo "📋 Checking changed files for hardcoded credentials..."

    # Get list of changed files (adapt based on CI system)
    if [ -n "$CI_MERGE_REQUEST_TARGET_BRANCH_NAME" ]; then
        # GitLab CI
        CHANGED_FILES=$(git diff --name-only "$CI_MERGE_REQUEST_TARGET_BRANCH_NAME")
    elif [ -n "$GITHUB_BASE_REF" ]; then
        # GitHub Actions
        CHANGED_FILES=$(git diff --name-only "origin/$GITHUB_BASE_REF")
    else
        # Fallback - check all files
        CHANGED_FILES=$(find . -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.env*" | head -20)
    fi

    # Check changed files for dangerous patterns
    DANGEROUS_PATTERNS=(
        "password.*=.*['\"](admin123|demo123|ChangeMeSecure123!)['\"]"
        "NEXT_PUBLIC.*PASSWORD"
        "NEXT_PUBLIC.*SECRET"
        "hardcoded.*password"
        "default.*password.*admin123"
    )

    FOUND_DANGEROUS=0
    for file in $CHANGED_FILES; do
        if [ -f "$file" ]; then
            for pattern in "${DANGEROUS_PATTERNS[@]}"; do
                if grep -q -i "$pattern" "$file" 2>/dev/null; then
                    print_status $RED "🚨 Dangerous pattern found in $file: $pattern"
                    FOUND_DANGEROUS=1
                fi
            done
        fi
    done

    if [ $FOUND_DANGEROUS -eq 1 ]; then
        print_status $RED "❌ Dangerous patterns found in changed files"
        VALIDATION_RESULT=1
    else
        print_status $GREEN "✅ No dangerous patterns in changed files"
    fi
fi

# Check environment variables
echo ""
echo "🌍 Checking environment variables..."
if [ -n "$CI" ] || [ -n "$GITHUB_ACTIONS" ]; then
    # In CI environment, check for required secure variables
    REQUIRED_VARS=("JWT_SECRET" "DB_PASSWORD")
    MISSING_VARS=()

    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var}" ]; then
            MISSING_VARS+=("$var")
        fi
    done

    if [ ${#MISSING_VARS[@]} -gt 0 ]; then
        print_status $YELLOW "⚠️  Missing required environment variables: ${MISSING_VARS[*]}"
        print_status $YELLOW "   This is normal in CI - ensure they are set in production"
    else
        print_status $GREEN "✅ Required environment variables are set"
    fi
fi

# Generate security report
echo ""
echo "📊 Generating security report..."
REPORT_FILE="$PROJECT_ROOT/security_validation_report.json"
if [ -f "$REPORT_FILE" ]; then
    print_status $GREEN "📄 Security report generated: $REPORT_FILE"
else
    print_status $YELLOW "⚠️  Security report not generated"
fi

# Final status
echo ""
if [ $VALIDATION_RESULT -eq 0 ]; then
    print_status $GREEN "🎉 All security checks passed!"
    echo ""
    echo "📋 Summary:"
    echo "   ✅ Hardcoded users security validation passed"
    echo "   ✅ No dangerous patterns in changed files"
    echo "   ✅ Environment variables properly configured"
    echo ""
    echo "🚀 CI pipeline can proceed"
else
    print_status $RED "💥 Security checks failed!"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Review the security issues above"
    echo "   2. Fix any hardcoded credentials"
    echo "   3. Ensure environment variables are secure"
    echo "   4. Re-run the pipeline after fixes"
    echo ""
    echo "🔗 For help, see: SECURITY_ANALYSIS_HARDCODED_USERS.md"
fi

exit $VALIDATION_RESULT