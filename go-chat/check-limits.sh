#!/bin/bash

echo "🔍 CHECKING ACTUAL SYSTEM LIMITS"
echo "================================"

# Check current session limits
echo "📊 Current Session Limits:"
echo "   File descriptors: $(ulimit -n)"
echo "   Processes: $(ulimit -u)"

# Check system maximums
echo ""
echo "🖥️  System Maximums:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "   kern.maxfiles: $(sysctl -n kern.maxfiles)"
    echo "   kern.maxfilesperproc: $(sysctl -n kern.maxfilesperproc)"
    echo "   kern.ipc.somaxconn: $(sysctl -n kern.ipc.somaxconn)"
fi

# Check if our limit file is active
echo ""
echo "🔧 Permanent Optimizations:"
if [[ -f "/Library/LaunchDaemons/limit.maxfiles.plist" ]]; then
    echo "   ✅ Permanent limit file exists"
    sudo launchctl list | grep limit.maxfiles && echo "   ✅ Limit service is loaded" || echo "   ❌ Limit service not loaded"
else
    echo "   ❌ No permanent limit file found"
fi

# Test actual file opening
echo ""
echo "🧪 Testing File Descriptor Usage:"
lsof | wc -l | xargs echo "   Current open files:"
