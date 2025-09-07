#!/bin/bash

# PRE-COMMIT REALITY CHECK
# Ejecutar ANTES de cada commit para validar estado real

echo "🛡️ PRE-COMMIT REALITY CHECK"
echo "============================="

# 1. EJECUTAR DAILY CHECK PRIMERO
echo "📋 Running daily system check..."
./scripts/daily-check.sh
DAILY_CHECK_STATUS=$?

if [ $DAILY_CHECK_STATUS -ne 0 ]; then
    echo ""
    echo "❌ COMMIT BLOCKED: Basic services not working"
    echo "🔧 Fix the failing services before committing"
    echo "💡 Run './scripts/daily-check.sh' to see details"
    exit 1
fi

# 2. VERIFICAR COMMIT MESSAGE
echo ""
echo "📝 Analyzing commit message..."

# Get the staged commit message (if using git commit -m)
COMMIT_MSG=""
if [ -f .git/COMMIT_EDITMSG ]; then
    COMMIT_MSG=$(cat .git/COMMIT_EDITMSG)
else
    # If no staged message, get the last commit (for post-commit validation)
    COMMIT_MSG=$(git log -1 --pretty=format:"%s" 2>/dev/null || echo "")
fi

if [ -z "$COMMIT_MSG" ]; then
    echo "⚠️  No commit message found - using interactive check"
    COMMIT_MSG="[Interactive Mode]"
fi

echo "Commit message: '$COMMIT_MSG'"

# 3. DETECTAR LENGUAJE ASPIRACIONAL
ASPIRATIONAL_WORDS="complete|finished|production-ready|enterprise-grade|100%|fully|totally|perfect|comprehensive"
COMPLETION_CLAIMS="sprint.*complete|day.*complete|module.*complete|system.*complete"

if [[ $COMMIT_MSG =~ $ASPIRATIONAL_WORDS ]] || [[ $COMMIT_MSG =~ $COMPLETION_CLAIMS ]]; then
    echo ""
    echo "⚠️  WARNING: Commit message contains completion claims"
    echo "🎯 Detected words: $(echo "$COMMIT_MSG" | grep -oE "$ASPIRATIONAL_WORDS|$COMPLETION_CLAIMS" | head -1)"
    echo ""
    echo "🎬 DEMO CHALLENGE:"
    echo "   Can you demonstrate this functionality right now?"
    echo "   - Open the app in browser"
    echo "   - Show the feature working"
    echo "   - Prove it handles edge cases"
    echo ""
    
    read -p "✅ I can demo this functionality live right now (y/N): " -n 1 -r
    echo ""
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "❌ COMMIT BLOCKED: Cannot demo claimed functionality"
        echo ""
        echo "🔄 SUGGESTED ALTERNATIVES:"
        echo "   Instead of: 'feat: complete user authentication'"
        echo "   Try: 'feat: add login form (validates email + password)'"
        echo ""
        echo "   Instead of: 'Sprint 8 Day 5 completed'"  
        echo "   Try: 'feat: implement user CRUD endpoints'"
        echo ""
        echo "💡 Rule: Only commit what you can demonstrate"
        exit 1
    else
        echo "✅ Demo challenge accepted - commit allowed"
    fi
fi

# 4. VERIFICAR ARCHIVOS MODIFICADOS
echo ""
echo "📂 Checking modified files..."

STAGED_FILES=$(git diff --cached --name-only 2>/dev/null || echo "")
if [ -n "$STAGED_FILES" ]; then
    echo "Modified files:"
    echo "$STAGED_FILES" | sed 's/^/   - /'
    
    # Verificar si hay cambios en documentación sin cambios en código
    DOC_CHANGES=$(echo "$STAGED_FILES" | grep -E '\.(md|txt|rst)$' | wc -l)
    CODE_CHANGES=$(echo "$STAGED_FILES" | grep -E '\.(py|ts|tsx|js|jsx)$' | wc -l)
    
    if [ $DOC_CHANGES -gt 0 ] && [ $CODE_CHANGES -eq 0 ]; then
        echo ""
        echo "⚠️  WARNING: Documentation-only changes detected"
        echo "🤔 Are you updating docs to match existing code?"
        echo ""
        read -p "✅ This documentation reflects working code (y/N): " -n 1 -r
        echo ""
        
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "❌ COMMIT BLOCKED: Documentation should reflect code reality"
            exit 1
        fi
    fi
else
    echo "⚠️  No staged files detected"
fi

# 5. VERIFICAR TESTS BÁSICOS SI EXISTEN
if [ -f "package.json" ] && grep -q '"test"' package.json; then
    echo ""
    echo "🧪 Running basic tests..."
    npm test -- --passWithNoTests --silent > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "⚠️  Some tests are failing - consider fixing before commit"
    else
        echo "✅ Basic tests passing"
    fi
fi

# 6. SUGERENCIAS PARA COMMIT MESSAGE
echo ""
echo "💡 COMMIT MESSAGE BEST PRACTICES:"
echo "   ✅ GOOD: 'feat: add user login form (validates email format)'"
echo "   ✅ GOOD: 'fix: resolve SQLAlchemy async context in user routes'"
echo "   ✅ GOOD: 'docs: update API documentation for working endpoints'"
echo ""
echo "   ❌ BAD: 'feat: complete enterprise authentication system'"
echo "   ❌ BAD: 'Sprint 8 Day 5 completed - all features working'"  
echo "   ❌ BAD: 'production-ready user management'"

# 7. RESULTADO FINAL
echo ""
echo "================================="
echo "✅ PRE-COMMIT CHECK: PASSED"
echo "🚀 Commit is ready to proceed"
echo ""
echo "📊 Next: Run './scripts/update-status.sh' after commit"
echo "🔄 Remember: Update CURRENT_STATUS.md reflects this change"

exit 0