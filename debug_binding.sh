#!/bin/bash

# Debug script for testing binding system
echo "🔍 Starting Binding Debug Test..."
echo "=================================="

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Set debug environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
export PYTHONUNBUFFERED=1

echo "🐍 Debug Options Available:"
echo "1. Run with PDB debugger (step-by-step)"
echo "2. Run with VS Code debugger (GUI)"
echo "3. Run simple test (no debugger)"
echo ""

read -p "Choose option (1-3): " choice

case $choice in
    1)
        echo "🔧 Running with PDB debugger..."
        echo "💡 Commands: 'n'=step over, 's'=step into, 'c'=continue, 'l'=list code"
        echo "=================================================="
        python debug_binding_pdb.py
        ;;
    2)
        echo "🖥️  Use VS Code debugger:"
        echo "   - Press F5 or go to Run & Debug"
        echo "   - Select 'Debug Binding Test (All Code)'"
        echo "   - Set breakpoints in your code"
        echo "   - Use 'justMyCode: false' to step into library code too"
        ;;
    3)
        echo "🧪 Running simple test..."
        echo "=================================================="
        python test_binding_debug.py
        ;;
    *)
        echo "❌ Invalid choice. Running simple test..."
        python test_binding_debug.py
        ;;
esac

echo "=================================="
echo "🏁 Debug test completed."
