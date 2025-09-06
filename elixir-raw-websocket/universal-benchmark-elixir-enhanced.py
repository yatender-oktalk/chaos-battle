#!/usr/bin/env python3
import asyncio
import websockets
import json
import time
import statistics
import os
from datetime import datetime
import signal
import sys

class EnhancedElixirWebSocketBenchmark:
    def __init__(self, config):
        self.config = config
        self.connections = []
        self.stats = {
            'connections_created': 0,
            'connections_failed': 0,
            'messages_sent': 0,
            'messages_failed': 0,
            'start_time': None,
            'errors': []
        }

        # Results storage (like Go benchmark)
        self.results = {
            'benchmark_info': {
                'test_name': config.get('test_name', 'elixir_test'),
                'description': config.get('description', 'Elixir WebSocket benchmark'),
                'timestamp': datetime.now().isoformat(),
                'server_url': config.get('server_url', 'ws://localhost:8081/socket/websocket'),
                'language': 'elixir',
                'framework': 'phoenix' if 'phoenix' in config.get('server_url', '') else 'raw'
            },
            'connection_test': {},
            'message_test': {},
            'endurance_test': {},
            'system_info': self.get_system_info()
        }

        # Create results directory
        self.results_dir = self.create_results_directory()

    def get_system_info(self):
        """Get system information"""
        import platform
        import psutil

        return {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'timestamp': datetime.now().isoformat()
        }

    def create_results_directory(self):
        """Create results directory structure like Go benchmark"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_name = self.config.get('test_name', 'elixir_test')

        session_dir = f"chaos-results/sessions/{timestamp}_{test_name}"
        os.makedirs(session_dir, exist_ok=True)

        return session_dir

    def save_results(self):
        """Save benchmark results to JSON file"""
        results_file = os.path.join(self.results_dir, f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.config.get('test_name', 'elixir')}.json")

        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"💾 Results saved: {results_file}")

        # Also create summary report
        self.create_summary_report()

        return results_file

    def create_summary_report(self):
        """Create markdown summary report"""
        report_file = os.path.join(self.results_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.config.get('test_name', 'elixir')}.md")

        with open(report_file, 'w') as f:
            f.write(f"# Elixir WebSocket Benchmark Report\n\n")
            f.write(f"**Test Name:** {self.results['benchmark_info']['test_name']}\n")
            f.write(f"**Framework:** {self.results['benchmark_info']['framework'].title()}\n")
            f.write(f"**Timestamp:** {self.results['benchmark_info']['timestamp']}\n")
            f.write(f"**Server URL:** {self.results['benchmark_info']['server_url']}\n\n")

            # Connection test results
            if self.results['connection_test']:
                conn = self.results['connection_test']
                f.write(f"## 🔥 Connection Test Results\n\n")
                f.write(f"- **Target:** {conn.get('target_connections', 0):,} connections\n")
                f.write(f"- **Achieved:** {conn.get('successful_connections', 0):,} ({conn.get('success_rate', 0):.1f}%)\n")
                f.write(f"- **Rate:** {conn.get('connection_rate', 0):.1f} conn/sec\n")
                f.write(f"- **Duration:** {conn.get('duration', 0):.2f}s\n")
                f.write(f"- **Failed:** {conn.get('failed_connections', 0):,}\n\n")

            # Message test results
            if self.results['message_test']:
                msg = self.results['message_test']
                f.write(f"## 🌊 Message Test Results\n\n")
                f.write(f"- **Target:** {msg.get('target_messages', 0):,} messages\n")
                f.write(f"- **Sent:** {msg.get('messages_sent', 0):,} ({msg.get('success_rate', 0):.1f}%)\n")
                f.write(f"- **Rate:** {msg.get('message_rate', 0):,.0f} msg/sec\n")
                f.write(f"- **Duration:** {msg.get('duration', 0):.2f}s\n")
                f.write(f"- **Errors:** {msg.get('messages_failed', 0):,}\n\n")

            # Endurance test results
            if self.results['endurance_test']:
                end = self.results['endurance_test']
                f.write(f"## 💪 Endurance Test Results\n\n")
                f.write(f"- **Duration:** {end.get('duration', 0):.1f}s\n")
                f.write(f"- **Messages:** {end.get('total_messages', 0):,}\n")
                f.write(f"- **Avg Rate:** {end.get('average_rate', 0):,.0f} msg/sec\n\n")

        print(f"📝 Report saved: {report_file}")

    async def connect_to_server(self, user_id):
        """Connect to server (Phoenix or Raw)"""
        try:
            url = self.config.get('server_url', 'ws://localhost:8081/socket/websocket')

            # Detect if this is raw WebSocket or Phoenix
            if 'raw_websocket' in self.config and self.config['raw_websocket']:
                return await self.connect_to_raw_websocket(user_id, url)
            else:
                return await self.connect_to_phoenix(user_id, url)

        except Exception as e:
            self.stats['connections_failed'] += 1
            self.stats['errors'].append(f"Connection error: {str(e)}")
            return None

    async def connect_to_raw_websocket(self, user_id, url):
        """Connect to raw Elixir WebSocket server"""
        try:
            # Raw WebSocket - direct connection
            websocket = await websockets.connect(f"{url}/{user_id}", ping_interval=None)
            self.stats['connections_created'] += 1
            return websocket
        except Exception as e:
            self.stats['connections_failed'] += 1
            return None

    async def connect_to_phoenix(self, user_id, url):
        """Connect to Phoenix WebSocket with proper handshake"""
        try:
            websocket = await websockets.connect(url, ping_interval=None)

            # Phoenix handshake - join channel
            join_message = {
                "topic": "chat:lobby",
                "event": "phx_join",
                "payload": {"id": user_id},
                "ref": f"join_{user_id}"
            }

            await websocket.send(json.dumps(join_message))

            # Wait for join confirmation
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            join_response = json.loads(response)

            if join_response.get('event') == 'phx_reply' and join_response.get('payload', {}).get('status') == 'ok':
                self.stats['connections_created'] += 1
                return websocket
            else:
                await websocket.close()
                self.stats['connections_failed'] += 1
                return None

        except Exception as e:
            self.stats['connections_failed'] += 1
            self.stats['errors'].append(f"Connection error: {str(e)}")
            return None

    async def send_message(self, websocket, content, sequence):
        """Send message (Phoenix or Raw)"""
        try:
            if 'raw_websocket' in self.config and self.config['raw_websocket']:
                # Raw WebSocket message
                message = {
                    "type": "benchmark_test",
                    "content": content,
                    "sequence": sequence,
                    "timestamp": time.time()
                }
            else:
                # Phoenix channel message
                message = {
                    "topic": "chat:lobby",
                    "event": "benchmark_test",
                    "payload": {
                        "content": content,
                        "sequence": sequence,
                        "timestamp": time.time()
                    },
                    "ref": f"msg_{sequence}"
                }

            await websocket.send(json.dumps(message))
            self.stats['messages_sent'] += 1
            return True

        except Exception as e:
            self.stats['messages_failed'] += 1
            self.stats['errors'].append(f"Message error: {str(e)}")
            return False

    async def connection_test(self):
        """Test maximum concurrent connections"""
        print(f"\n🔥 ELIXIR CONNECTION TEST")
        print("=" * 50)

        target = self.config['tests']['connection_test']['target_connections']
        batch_size = self.config['tests']['connection_test']['batch_size']
        timeout = self.config['tests']['connection_test']['connection_timeout']

        print(f"🎯 Target: {target:,} connections")
        print(f"📦 Batch size: {batch_size}")
        print(f"⏱️ Timeout: {timeout}s")

        start_time = time.time()

        for i in range(0, target, batch_size):
            batch_end = min(i + batch_size, target)
            print(f"📊 Progress: {i:,}/{target:,} connections ({(i/target*100):.1f}%)", end='\r')

            # Create batch of connections
            batch_tasks = []
            for j in range(i, batch_end):
                user_id = f"user_{j}"
                task = asyncio.create_task(self.connect_to_server(user_id))
                batch_tasks.append(task)

            # Wait for batch with timeout
            try:
                batch_results = await asyncio.wait_for(
                    asyncio.gather(*batch_tasks, return_exceptions=True),
                    timeout=timeout
                )

                # Store successful connections
                for result in batch_results:
                    if result and not isinstance(result, Exception):
                        self.connections.append(result)

            except asyncio.TimeoutError:
                print(f"\n⚠️ Batch timeout at {i:,} connections")
                for task in batch_tasks:
                    task.cancel()

            # Rate limiting
            await asyncio.sleep(0.01)

            # Check failure threshold
            failure_rate = self.stats['connections_failed'] / max(1, self.stats['connections_created'] + self.stats['connections_failed'])
            if failure_rate > self.config['tests']['connection_test']['failure_threshold']:
                print(f"\n⚠️ High failure rate ({failure_rate:.1%}), stopping test")
                break

        elapsed = time.time() - start_time
        successful = len(self.connections)
        rate = successful / elapsed if elapsed > 0 else 0

        # Store results
        self.results['connection_test'] = {
            'target_connections': target,
            'successful_connections': successful,
            'failed_connections': self.stats['connections_failed'],
            'success_rate': (successful / target * 100) if target > 0 else 0,
            'connection_rate': rate,
            'duration': elapsed,
            'batch_size': batch_size,
            'timeout': timeout
        }

        print(f"\n📊 ELIXIR CONNECTION RESULTS:")
        print(f"   ✅ Achieved: {successful:,}/{target:,} ({successful/target*100:.1f}%)")
        print(f"   ⚡ Rate: {rate:.1f} conn/sec")
        print(f"   ⏱️ Time: {elapsed:.2f}s")
        print(f"   ❌ Failed: {self.stats['connections_failed']:,}")

    async def message_test(self):
        """Test message throughput"""
        if not self.connections:
            print("❌ No connections available for message test")
            return

        print(f"\n🌊 ELIXIR MESSAGE TEST")
        print("=" * 50)

        active_connections = len(self.connections)
        multiplier = self.config['tests']['message_test']['target_multiplier']
        target_messages = active_connections * multiplier
        batch_size = self.config['tests']['message_test']['batch_size']

        print(f"🎯 Target: {target_messages:,} messages")
        print(f"📦 Batch size: {batch_size}")
        print(f"💪 Using: {active_connections:,} connections")

        start_time = time.time()

        for i in range(0, target_messages, batch_size):
            batch_end = min(i + batch_size, target_messages)

            # Create message batch
            batch_tasks = []
            for j in range(i, batch_end):
                connection = self.connections[j % active_connections]
                content = f"benchmark_message_{j}" * self.config['tests']['message_test']['message_size_multiplier']

                task = asyncio.create_task(self.send_message(connection, content, j))
                batch_tasks.append(task)

            # Execute batch
            await asyncio.gather(*batch_tasks, return_exceptions=True)

            # Progress update
            elapsed = time.time() - start_time
            rate = self.stats['messages_sent'] / elapsed if elapsed > 0 else 0
            print(f"📊 Progress: {self.stats['messages_sent']:,}/{target_messages:,} ({rate:.0f} msg/sec)", end='\r')

            # Check error threshold
            if self.stats['messages_failed'] > self.config['tests']['message_test']['error_threshold']:
                print(f"\n⚠️ Too many errors ({self.stats['messages_failed']:,}), stopping test")
                break

            await asyncio.sleep(0.001)

        elapsed = time.time() - start_time
        rate = self.stats['messages_sent'] / elapsed if elapsed > 0 else 0

        # Store results
        self.results['message_test'] = {
            'target_messages': target_messages,
            'messages_sent': self.stats['messages_sent'],
            'messages_failed': self.stats['messages_failed'],
            'success_rate': (self.stats['messages_sent'] / target_messages * 100) if target_messages > 0 else 0,
            'message_rate': rate,
            'duration': elapsed,
            'active_connections': active_connections,
            'batch_size': batch_size
        }

        print(f"\n📊 ELIXIR MESSAGE RESULTS:")
        print(f"   ✅ Sent: {self.stats['messages_sent']:,}/{target_messages:,} ({self.stats['messages_sent']/target_messages*100:.1f}%)")
        print(f"   ⚡ Rate: {rate:,.0f} msg/sec")
        print(f"   ❌ Errors: {self.stats['messages_failed']:,}")
        print(f"   ⏱️ Time: {elapsed:.2f}s")

    async def endurance_test(self):
        """Test sustained performance - MAXIMUM THROUGHPUT"""
        if not self.connections:
            print("❌ No connections available for endurance test")
            return

        print(f"\n💪 ELIXIR ENDURANCE TEST")
        print("=" * 50)

        duration = self.config['tests']['endurance_test']['duration']
        checkpoint_interval = self.config['tests']['endurance_test']['checkpoint_interval']
        messages_per_batch = self.config['tests']['endurance_test']['messages_per_batch']

        print(f"🎯 Duration: {duration} seconds")
        print(f"📊 Checkpoint interval: {checkpoint_interval}s")

        start_time = time.time()
        last_checkpoint = start_time
        total_endurance_messages = 0
        rates = []
        checkpoint_start_messages = 0

        while time.time() - start_time < duration:
            # Send batch of messages AS FAST AS POSSIBLE
            batch_tasks = []
            for i in range(messages_per_batch):
                connection = self.connections[i % len(self.connections)]
                content = f"endurance_msg_{total_endurance_messages + i}"

                task = asyncio.create_task(self.send_message(connection, content, total_endurance_messages + i))
                batch_tasks.append(task)

            await asyncio.gather(*batch_tasks, return_exceptions=True)
            total_endurance_messages += messages_per_batch

            # Checkpoint reporting
            current_time = time.time()
            if current_time - last_checkpoint >= checkpoint_interval:
                # Calculate ACTUAL throughput for this checkpoint period
                messages_in_period = total_endurance_messages - checkpoint_start_messages
                period_duration = current_time - last_checkpoint
                checkpoint_rate = messages_in_period / period_duration
                rates.append(checkpoint_rate)

                total_elapsed = current_time - start_time
                overall_rate = total_endurance_messages / total_elapsed

                print(f"💪 ENDURANCE [{int(total_elapsed)}s]: {total_endurance_messages:,} msgs ({checkpoint_rate:,.0f}/sec, overall: {overall_rate:,.0f}/sec)")

                last_checkpoint = current_time
                checkpoint_start_messages = total_endurance_messages

            # REMOVE OR MINIMIZE THE SLEEP - this was throttling you!
            # await asyncio.sleep(0.01)  # ← DELETE THIS LINE or make it much smaller
            await asyncio.sleep(0.001)  # Much smaller delay

        final_elapsed = time.time() - start_time
        actual_rate = total_endurance_messages / final_elapsed

        # Store results
        self.results['endurance_test'] = {
            'duration': final_elapsed,
            'total_messages': total_endurance_messages,
            'average_rate': actual_rate,
            'checkpoint_rates': rates,
            'messages_per_batch': messages_per_batch,
            'checkpoint_interval': checkpoint_interval
        }

        print(f"💪 ELIXIR ENDURANCE RESULTS:")
        print(f"   ⏱️ Duration: {final_elapsed:.1f}s")
        print(f"   📊 Messages: {total_endurance_messages:,}")
        print(f"   🚀 Avg Rate: {actual_rate:,.0f} msg/sec")

    async def cleanup(self):
        """Clean up connections"""
        print(f"\n🧹 Cleaning up {len(self.connections):,} connections...")

        close_tasks = []
        for conn in self.connections:
            if conn and not conn.closed:
                close_tasks.append(asyncio.create_task(conn.close()))

        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)

        self.connections.clear()

    async def run_benchmark(self):
        """Run complete benchmark suite"""
        self.stats['start_time'] = time.time()

        try:
            if self.config['tests']['connection_test']['enabled']:
                await self.connection_test()

            if self.config['tests']['message_test']['enabled']:
                await self.message_test()

            if self.config['tests']['endurance_test']['enabled']:
                await self.endurance_test()

        except KeyboardInterrupt:
            print("\n🛑 Benchmark interrupted by user")
        finally:
            await self.cleanup()

        # Save results
        results_file = self.save_results()

        print(f"\n🎉 ELIXIR BENCHMARK COMPLETE!")
        print(f"📁 Results: {self.results_dir}")

async def main():
    if len(sys.argv) != 2:
        print("Usage: python universal-benchmark-elixir-enhanced.py <config.json>")
        sys.exit(1)

    config_file = sys.argv[1]

    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"❌ Config file not found: {config_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config file: {e}")
        sys.exit(1)

    # Install required package if not available
    try:
        import psutil
    except ImportError:
        print("Installing psutil for system info...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        import psutil

    benchmark = EnhancedElixirWebSocketBenchmark(config)
    await benchmark.run_benchmark()

if __name__ == "__main__":
    asyncio.run(main())
