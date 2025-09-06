#!/usr/bin/env python3

import asyncio
import websockets
import json
import subprocess
import time
import requests
import os
import signal
import psutil
from datetime import datetime

class GoServerChaosTest:
    def __init__(self):
        self.server_process = None
        self.base_url = "http://localhost:8080"
        self.ws_url = "ws://localhost:8080/ws"
        self.connections = []
        
    async def start_server(self):
        """Start the Go server"""
        print("🚀 Starting Go server...")
        self.server_process = subprocess.Popen(
            ['./go-chat'],
            cwd='.',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        for i in range(10):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=2)
                if response.status_code == 200:
                    print("✅ Server started successfully")
                    return True
            except:
                await asyncio.sleep(1)
                
        print("❌ Server failed to start")
        return False
        
    def stop_server(self):
        """Stop the Go server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            self.server_process = None
            
    async def create_connections(self, count=10):
        """Create multiple WebSocket connections"""
        print(f"📡 Creating {count} connections...")
        
        for i in range(count):
            try:
                ws = await websockets.connect(f"{self.ws_url}?id=user_{i}")
                self.connections.append(ws)
                
                # Send initial message
                message = {
                    "type": "chat",
                    "content": f"Hello from user_{i}"
                }
                await ws.send(json.dumps(message))
                
            except Exception as e:
                print(f"❌ Failed to connect user_{i}: {e}")
                
        print(f"✅ Created {len(self.connections)} connections")
        return len(self.connections)
        
    async def check_connection_health(self):
        """Check how many connections are still alive"""
        alive = 0
        for ws in self.connections:
            try:
                await asyncio.wait_for(ws.ping(), timeout=1.0)
                alive += 1
            except:
                pass
        return alive
        
    def get_server_stats(self):
        """Get server statistics"""
        try:
            # Health stats
            health_response = requests.get(f"{self.base_url}/health", timeout=2)
            health_data = health_response.json() if health_response.status_code == 200 else {}
            
            # Process stats
            process_stats = {}
            if self.server_process:
                try:
                    p = psutil.Process(self.server_process.pid)
                    process_stats = {
                        'cpu_percent': p.cpu_percent(),
                        'memory_mb': p.memory_info().rss / 1024 / 1024,
                        'status': p.status()
                    }
                except:
                    pass
                    
            return {
                'health': health_data,
                'process': process_stats,
                'timestamp': datetime.now().isoformat()
            }
        except:
            return {'error': 'Could not get stats'}
            
    async def chaos_test_process_kill(self):
        """Test 1: Kill the server process and measure recovery"""
        print("\n🔥 CHAOS TEST 1: Process Kill")
        print("=" * 40)
        
        # Get baseline
        baseline_connections = await self.check_connection_health()
        baseline_stats = self.get_server_stats()
        print(f"📊 Baseline: {baseline_connections} alive connections")
        
        # Kill the process
        print("💀 Killing server process...")
        kill_time = time.time()
        
        if self.server_process:
            self.server_process.kill()
            self.server_process.wait()
            
        # Measure downtime
        print("⏱️  Measuring downtime...")
        downtime = 0
        max_downtime = 30  # seconds
        
        for i in range(max_downtime):
            await asyncio.sleep(1)
            downtime += 1
            
            # Check if someone manually restarts it
            try:
                response = requests.get(f"{self.base_url}/health", timeout=1)
                if response.status_code == 200:
                    recovery_time = time.time() - kill_time
                    print(f"✅ Server recovered after {recovery_time:.2f}s")
                    break
            except:
                continue
        else:
            print(f"❌ Server did not recover within {max_downtime}s")
            recovery_time = max_downtime
            
        # Check connection survival
        surviving_connections = await self.check_connection_health()
        connections_lost = baseline_connections - surviving_connections
        
        result = {
            'test': 'process_kill',
            'baseline_connections': baseline_connections,
            'surviving_connections': surviving_connections,
            'connections_lost': connections_lost,
            'recovery_time': recovery_time,
            'baseline_stats': baseline_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"📊 Results:")
        print(f"   - Recovery time: {recovery_time:.2f}s")
        print(f"   - Connections lost: {connections_lost}/{baseline_connections}")
        if baseline_connections > 0:
            print(f"   - Survival rate: {(surviving_connections/baseline_connections)*100:.1f}%")
        
        return result
        
    async def chaos_test_connection_flood(self):
        """Test 2: Flood server with connections"""
        print("\n🌊 CHAOS TEST 2: Connection Flood")
        print("=" * 40)
        
        baseline_connections = await self.check_connection_health()
        baseline_stats = self.get_server_stats()
        
        print(f"📊 Baseline: {baseline_connections} connections")
        print("🚀 Starting connection flood...")
        
        flood_start = time.time()
        flood_connections = []
        successful_floods = 0
        
        # Try to create 100 rapid connections
        for i in range(100):
            try:
                ws = await asyncio.wait_for(
                    websockets.connect(f"{self.ws_url}?id=flood_{i}"),
                    timeout=2.0
                )
                flood_connections.append(ws)
                successful_floods += 1
                
                if i % 20 == 0:
                    await asyncio.sleep(0.1)  # Brief pause
                    
            except Exception as e:
                if i < 10:  # Only show first few errors
                    print(f"❌ Flood connection {i} failed: {e}")
                break
                
        flood_time = time.time() - flood_start
        
        # Check impact on original connections
        surviving_original = await self.check_connection_health()
        connections_lost = baseline_connections - surviving_original
        
        # Get server stats under load
        load_stats = self.get_server_stats()
        
        # Clean up flood connections
        print("🧹 Cleaning up flood connections...")
        for ws in flood_connections:
            try:
                await ws.close()
            except:
                pass
                
        result = {
            'test': 'connection_flood',
            'baseline_connections': baseline_connections,
            'successful_floods': successful_floods,
            'flood_time': flood_time,
            'surviving_original': surviving_original,
            'connections_lost': connections_lost,
            'baseline_stats': baseline_stats,
            'load_stats': load_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"📊 Results:")
        print(f"   - Successful floods: {successful_floods}/100")
        print(f"   - Flood time: {flood_time:.2f}s")
        print(f"   - Original connections lost: {connections_lost}")
        if flood_time > 0:
            print(f"   - Flood rate: {successful_floods/flood_time:.1f} conn/sec")
        
        return result
        
    async def chaos_test_message_spam(self):
        """Test 3: Spam messages and measure performance"""
        print("\n📢 CHAOS TEST 3: Message Spam")
        print("=" * 40)
        
        baseline_stats = self.get_server_stats()
        print("🚀 Starting message spam...")
        
        spam_start = time.time()
        messages_sent = 0
        
        # Send 1000 messages rapidly
        for i in range(1000):
            try:
                if self.connections:
                    ws = self.connections[i % len(self.connections)]
                    message = {
                        "type": "spam",
                        "content": f"Spam message {i} - " + "x" * 100  # Make it bigger
                    }
                    await ws.send(json.dumps(message))
                    messages_sent += 1
                    
                    if i % 100 == 0:
                        await asyncio.sleep(0.01)  # Brief pause
                        
            except Exception as e:
                if i < 10:  # Only show first few errors
                    print(f"❌ Message {i} failed: {e}")
                break
                
        spam_time = time.time() - spam_start
        
        # Wait a bit and check server health
        await asyncio.sleep(2)
        final_stats = self.get_server_stats()
        surviving_connections = await self.check_connection_health()
        
        result = {
            'test': 'message_spam',
            'messages_sent': messages_sent,
            'spam_time': spam_time,
            'message_rate': messages_sent / spam_time if spam_time > 0 else 0,
            'surviving_connections': surviving_connections,
            'baseline_stats': baseline_stats,
            'final_stats': final_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"📊 Results:")
        print(f"   - Messages sent: {messages_sent}/1000")
        print(f"   - Spam time: {spam_time:.2f}s")
        print(f"   - Message rate: {result['message_rate']:.1f} msg/sec")
        print(f"   - Connections surviving: {surviving_connections}")
        
        return result
        
    async def run_all_chaos_tests(self):
        """Run the complete chaos test suite"""
        print("🔥 GO CHAT SERVER CHAOS TESTING")
        print("=" * 50)
        
        results = []
        
        try:
            # Start server
            if not await self.start_server():
                return []
                
            # Create baseline connections
            await self.create_connections(20)
            await asyncio.sleep(2)  # Let connections stabilize
            
            # Run chaos tests
            print(f"\n🎯 Running chaos tests...")
            
            # Test 1: Connection Flood
            results.append(await self.chaos_test_connection_flood())
            await asyncio.sleep(2)
            
            # Test 2: Message Spam
            results.append(await self.chaos_test_message_spam())
            await asyncio.sleep(2)
            
            # Test 3: Process Kill (requires manual restart)
            results.append(await self.chaos_test_process_kill())
            
        finally:
            # Cleanup
            print("\n🧹 Cleaning up...")
            for ws in self.connections:
                try:
                    await ws.close()
                except:
                    pass
            self.stop_server()
            
        return results
        
    def generate_report(self, results):
        """Generate a summary report"""
        print("\n" + "=" * 50)
        print("🏆 CHAOS TEST RESULTS SUMMARY")
        print("=" * 50)
        
        for result in results:
            test_name = result['test'].replace('_', ' ').title()
            print(f"\n📊 {test_name}:")
            
            if result['test'] == 'process_kill':
                print(f"   Recovery Time: {result['recovery_time']:.2f}s")
                print(f"   Connection Loss: {result['connections_lost']}/{result['baseline_connections']}")
                
            elif result['test'] == 'connection_flood':
                print(f"   Successful Floods: {result['successful_floods']}/100")
                if result['flood_time'] > 0:
                    print(f"   Flood Rate: {result['successful_floods']/result['flood_time']:.1f} conn/sec")
                print(f"   Original Connections Lost: {result['connections_lost']}")
                
            elif result['test'] == 'message_spam':
                print(f"   Messages Sent: {result['messages_sent']}/1000")
                print(f"   Message Rate: {result['message_rate']:.1f} msg/sec")
                print(f"   Connections Survived: {result['surviving_connections']}")
                
        print(f"\n✅ Go server chaos testing complete!")
        return results

async def main():
    chaos_test = GoServerChaosTest()
    results = await chaos_test.run_all_chaos_tests()
    chaos_test.generate_report(results)

if __name__ == "__main__":
    asyncio.run(main())
