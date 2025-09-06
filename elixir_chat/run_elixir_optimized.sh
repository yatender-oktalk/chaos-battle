#!/bin/bash

echo "🔥 Starting Elixir Chat Server with MAXIMUM OPTIMIZATION"

# Set system limits
ulimit -n 100000
echo "📈 File descriptor limit: $(ulimit -n)"

# Get system info for optimal configuration
LOGICAL_CPUS=$(sysctl -n hw.logicalcpu 2>/dev/null || nproc 2>/dev/null || echo "8")
SCHEDULERS=$((LOGICAL_CPUS > 16 ? 16 : LOGICAL_CPUS))
DIRTY_CPU_SCHEDULERS=$((SCHEDULERS / 2))
if [ $DIRTY_CPU_SCHEDULERS -lt 1 ]; then
    DIRTY_CPU_SCHEDULERS=1
fi

echo "🖥️  System CPUs: $LOGICAL_CPUS"
echo "⚙️  Schedulers: $SCHEDULERS"
echo "🔧 Dirty CPU Schedulers: $DIRTY_CPU_SCHEDULERS"

# Optimized BEAM VM settings for your M2 Pro
export ERL_OPTS="+P 2000000 +Q 1000000 +K true +A 256 +S $SCHEDULERS:$SCHEDULERS +SDcpu $DIRTY_CPU_SCHEDULERS:$DIRTY_CPU_SCHEDULERS +SDio 8 +sbt db +sub true +swt very_high +sss 256 +sssdcpu 64 +sssdio 64"

echo ""
echo "🚀 BEAM VM Optimizations:"
echo "   +P 2000000           # Max processes: 2 million"
echo "   +Q 1000000           # Max ports: 1 million" 
echo "   +K true              # Enable kernel poll"
echo "   +A 256               # Async threads: 256"
echo "   +S $SCHEDULERS:$SCHEDULERS         # Scheduler threads: $SCHEDULERS"
echo "   +SDcpu $DIRTY_CPU_SCHEDULERS:$DIRTY_CPU_SCHEDULERS     # Dirty CPU schedulers: $DIRTY_CPU_SCHEDULERS"
echo "   +SDio 8              # Dirty IO schedulers: 8"
echo "   +sbt db              # Scheduler bind type: database"
echo "   +sub true            # Scheduler utilization balancing"
echo "   +swt very_high       # Scheduler wakeup threshold: very high"
echo "   +sss 256             # Scheduler stack size: 256KB"
echo "   +sssdcpu 64          # Dirty CPU stack size: 64KB"
echo "   +sssdio 64           # Dirty IO stack size: 64KB"

echo ""
echo "🎯 Starting Phoenix server on port 8081..."
echo "🌐 WebSocket endpoint: ws://localhost:8081/socket/websocket"
echo "📊 Health check: http://localhost:8081/health"
echo "📈 Stats: http://localhost:8081/stats"
echo ""

# Start with production environment for maximum performance
MIX_ENV=prod mix phx.server
