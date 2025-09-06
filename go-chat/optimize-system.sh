#!/bin/bash

echo "🔧 OPTIMIZING SYSTEM FOR CHAOS TESTING (Admin Mode)"
echo "=================================================="

# Check current limits
echo "📊 Current System Limits:"
echo "   File descriptors: $(ulimit -n)"
echo "   Processes: $(ulimit -u)"
echo "   Max files (system): $(sysctl -n kern.maxfiles 2>/dev/null || echo 'N/A')"

# macOS specific optimizations
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Detected macOS - Applying macOS optimizations..."
    
    # Temporary session limits
    ulimit -n 65536
    ulimit -u 4096
    
    # System-wide optimizations (requires admin)
    echo "🔐 Applying system-wide optimizations (requires sudo)..."
    
    # Network optimizations
    sudo sysctl -w net.inet.tcp.msl=1000
    sudo sysctl -w net.inet.tcp.sendspace=65536
    sudo sysctl -w net.inet.tcp.recvspace=65536
    sudo sysctl -w kern.ipc.somaxconn=2048
    
    # Memory optimizations
    sudo sysctl -w vm.pressure_disable_threshold=15
    
    # Create permanent limit file
    sudo tee /Library/LaunchDaemons/limit.maxfiles.plist > /dev/null << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"\>
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>limit.maxfiles</string>
    <key>ProgramArguments</key>
    <array>
        <string>launchctl</string>
        <string>limit</string>
        <string>maxfiles</string>
        <string>65536</string>
        <string>65536</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
PLIST
    
    # Load the limits
    sudo launchctl load -w /Library/LaunchDaemons/limit.maxfiles.plist 2>/dev/null || echo "   (Will take effect after reboot)"
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Detected Linux - Applying Linux optimizations..."
    
    # Session limits
    ulimit -n 65536
    ulimit -u 4096
    
    # System optimizations
    echo "🔐 Applying system optimizations..."
    
    # Network optimizations
    sudo sysctl -w net.core.somaxconn=2048
    sudo sysctl -w net.ipv4.tcp_max_syn_backlog=2048
    sudo sysctl -w net.core.netdev_max_backlog=5000
    sudo sysctl -w net.ipv4.tcp_fin_timeout=15
    sudo sysctl -w net.ipv4.tcp_tw_reuse=1
    
    # File descriptor limits
    echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
    echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf
    echo "* soft nproc 4096" | sudo tee -a /etc/security/limits.conf
    echo "* hard nproc 4096" | sudo tee -a /etc/security/limits.conf
    
fi

# Verify new limits
echo ""
echo "✅ Optimized System Limits:"
echo "   File descriptors: $(ulimit -n)"
echo "   Processes: $(ulimit -u)"

# System info
echo ""
echo "💻 System Information:"
if command -v nproc &> /dev/null; then
    echo "   CPU cores: $(nproc)"
elif command -v sysctl &> /dev/null; then
    echo "   CPU cores: $(sysctl -n hw.ncpu)"
fi

if command -v free &> /dev/null; then
    echo "   Memory: $(free -h | awk '/^Mem:/ {print $2}')"
elif command -v sysctl &> /dev/null; then
    echo "   Memory: $(echo "$(sysctl -n hw.memsize) / 1073741824" | bc 2>/dev/null || echo "Unknown")GB"
fi

echo "   Architecture: $(uname -m)"
echo "   OS: $(uname -s)"

echo ""
echo "🎯 System optimization complete!"
echo "🔥 Ready for EXTREME chaos testing!"
