#!/bin/bash

echo "🐳 DOCKER PORT INVESTIGATION"
echo "============================"

echo ""
echo "📊 DOCKER PROCESSES:"
docker ps -a

echo ""
echo "📊 DOCKER NETWORKS:"
docker network ls

echo ""
echo "📊 DOCKER PORT BINDINGS:"
docker ps --format "table {{.Names}}\t{{.Ports}}"

echo ""
echo "📊 DOCKER BRIDGE NETWORK USAGE:"
ifconfig | grep -A 5 docker

echo ""
echo "📊 CONNECTIONS TO DOCKER NETWORKS:"
netstat -rn | grep docker
