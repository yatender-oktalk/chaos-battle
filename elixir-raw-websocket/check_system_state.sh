#!/bin/bash

echo "🔍 SYSTEM STATE INVESTIGATION"
echo "============================="

echo ""
echo "📡 PORT RANGE SETTINGS:"
sysctl net.inet.ip.portrange.first
sysctl net.inet.ip.portrange.last
AVAILABLE_PORTS=$(($(sysctl -n net.inet.ip.portrange.last) - $(sysctl -n net.inet.ip.portrange.first)))
echo "Available ports: $AVAILABLE_PORTS"

echo ""
echo "📁 FILE DESCRIPTOR LIMITS:"
echo "Current ulimit -n: $(ulimit -n)"
sysctl kern.maxfiles
sysctl kern.maxfilesperproc

echo ""
echo "🌐 NETWORK SETTINGS:"
sysctl kern.ipc.somaxconn
sysctl kern.ipc.maxsockbuf
sysctl net.inet.tcp.sendspace
sysctl net.inet.tcp.recvspace

echo ""
echo "💾 MEMORY & PROCESS LIMITS:"
sysctl kern.maxproc
sysctl kern.maxprocperuid

echo ""
echo "🔍 CURRENT PROCESS COUNT:"
ps aux | wc -l

echo ""
echo "📊 CURRENT NETWORK CONNECTIONS:"
netstat -an | grep ESTABLISHED | wc -l

echo ""
echo "🧠 AVAILABLE MEMORY:"
vm_stat | head -10
