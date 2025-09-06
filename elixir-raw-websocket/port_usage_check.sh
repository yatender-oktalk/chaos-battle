#!/bin/bash

echo "🔍 PORT USAGE ANALYSIS"
echo "====================="

echo ""
echo "📊 CURRENT PORT USAGE BY STATE:"
netstat -an | awk '/tcp/ {print $6}' | sort | uniq -c | sort -nr

echo ""
echo "📊 CONNECTIONS TO PORT 8081:"
netstat -an | grep :8081 | wc -l

echo ""
echo "📊 OUTBOUND CONNECTIONS FROM HIGH PORTS:"
netstat -an | awk '/tcp.*\.[0-9]+:([4-6][0-9][0-9][0-9][0-9]|[0-9][0-9][0-9][0-9]).*ESTABLISHED/ {count++} END {print "High port connections:", count+0}'

echo ""
echo "📊 TOP 10 PROCESSES BY OPEN FILES:"
lsof | awk '{print $2}' | sort | uniq -c | sort -nr | head -10

echo ""
echo "🔍 ELIXIR BEAM PROCESSES:"
ps aux | grep beam
