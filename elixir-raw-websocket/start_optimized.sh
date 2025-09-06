#!/bin/bash

echo "🔥 Starting Elixir WebSocket Server with VM Optimizations"
echo "=================================================="

export ERL_FLAGS="+A 128 +K true +P 2000000 +Q 1048576 +zdbbl 65536 +sbt db +S 8:8 +SDcpu 8:8 +SDio 8"

echo "⚡ VM Args: $ERL_FLAGS"
echo "🚀 Starting server..."

mix run --no-halt
