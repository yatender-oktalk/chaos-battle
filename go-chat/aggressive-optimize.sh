#!/bin/bash

echo "🚀 AGGRESSIVE OPTIMIZATION MODE"
echo "==============================="

# Force higher limits in current session
ulimit -n 100000  # Try for 100K file descriptors
ulimit -u 8192    # More processes

echo "📊 New Session Limits:"
echo "   File descriptors: $(ulimit -n)"
echo "   Processes: $(ulimit -u)"

# More aggressive system settings
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🔧 Applying aggressive macOS settings..."
    
    # Network optimizations
    sudo sysctl -w net.inet.tcp.msl=500
    sudo sysctl -w net.inet.tcp.sendspace=131072
    sudo sysctl -w net.inet.tcp.recvspace=131072
    sudo sysctl -w kern.ipc.somaxconn=4096
    sudo sysctl -w kern.ipc.maxsockbuf=8388608
    
    # More file descriptors
    sudo sysctl -w kern.maxfiles=200000
    sudo sysctl -w kern.maxfilesperproc=100000
    
    echo "✅ Aggressive optimizations applied!"
fi

# Export for subprocesses
export RLIMIT_NOFILE=100000

echo "🎯 Ready for MAXIMUM PERFORMANCE testing!"
