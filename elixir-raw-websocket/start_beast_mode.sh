#!/bin/bash

echo "🔥 Starting ElixirRawWebsocket in BEAST MODE!"
echo "================================================"

# Set environment variables for maximum performance
export MIX_ENV=prod
export ELIXIR_ERL_OPTIONS="+K true +A 1024 +P 10000000 +Q 2097152"
export ERL_MAX_ETS_TABLES=50000
export ERL_CRASH_DUMP_SECONDS=0

echo "🚀 Environment configured for MAXIMUM PERFORMANCE"
echo "⚡ Process limit: 10,000,000"
echo "🔧 Async threads: 1024" 
echo "📡 Kernel polling: enabled"
echo "💾 ETS tables: 50,000"

echo ""
echo "🎯 Starting server on port 8081..."
echo "🌐 WebSocket endpoint: ws://localhost:8081/ws"
echo ""

# Start with optimized settings
iex --erl "+K true +A 1024 +P 10000000 +Q 1000000" -S mix run --no-halt
