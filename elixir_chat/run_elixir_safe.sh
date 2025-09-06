#!/bin/bash

echo "🔥 Starting Elixir Chat Server - SAFE CONFIGURATION"

# Set system limits
ulimit -n 100000
echo "📈 File descriptor limit: $(ulimit -n)"

# Conservative but high-performance settings
export ERL_OPTS="+P 2000000 +Q 1000000 +K true +A 128 +S 8:8 +SDcpu 4:4 +SDio 4 +sbt db"

echo ""
echo "🚀 BEAM VM Optimizations (Safe Mode):"
echo "   +P 2000000    # Max processes: 2 million"
echo "   +Q 1000000    # Max ports: 1 million" 
echo "   +K true       # Enable kernel poll"
echo "   +A 128        # Async threads: 128"
echo "   +S 8:8        # Scheduler threads: 8"
echo "   +SDcpu 4:4    # Dirty CPU schedulers: 4"
echo "   +SDio 4       # Dirty IO schedulers: 4"
echo "   +sbt db       # Scheduler bind type: database"

echo ""
echo "🎯 Starting Phoenix server on port 8081..."
echo "🌐 WebSocket endpoint: ws://localhost:8081/socket/websocket"
echo "📊 Health check: http://localhost:8081/health"
echo "📈 Stats: http://localhost:8081/stats"
echo ""

MIX_ENV=prod mix phx.server
