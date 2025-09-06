#!/usr/bin/env python3
"""
Universal Configurable Benchmark Suite
Load test parameters from JSON config files
"""

import asyncio
import websockets
import json
import subprocess
import time
import requests
import psutil
import platform
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path

class UniversalBenchmarkSuite:
    def __init__(self, config_file):
        # Load configuration
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.server_process = None
        self.base_url = "http://localhost:8080"
        self.ws_url = "ws://localhost:8080/ws"
        self.connections = []
        
        # Create session directory
        config_name = Path(config_file).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = f"{timestamp}_{config_name}_{self.config['test_name']}"
        self.results_dir = Path(f"chaos-results/sessions/{self.session_id}")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize results storage
        self.session_data = {
            'session_id': self.session_id,
            'config_used': self.config,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'system_info': self.get_system_info(),
            'test_results': [],
            'performance_timeline': [],
            'summary': {}
        }
        
        print(f"🔧 Loaded config: {self.config['test_name']}")
        print(f"📝 Description: {self.config['description']}")
        
    def get_system_info(self):
        """Get system information"""
        try:
            return {
                'os': platform.system(),
                'processor': 'Apple M2 Pro',
                'cpu_cores': psutil.cpu_count(logical=False),
                'cpu_threads': psutil.cpu_count(logical=True),
                'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'file_descriptor_limit': 100000,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def start_server(self):
        """Start the Go server"""
        print("🚀 Starting Go server...")
        start_time = time.time()
        
        self.server_process = subprocess.Popen(
            ['./go-chat'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server with configurable timeout
        timeout = self.config.get('server_startup_timeout', 10)
        for i in range(timeout):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=2)
                if response.status_code == 200:
                    startup_time = time.time() - start_time
                    print(f"✅ Server ready in {startup_time:.2f}s")
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
    
    async def create_single_connection(self, user_id):
        """Create a single WebSocket connection"""
        connection_config = self.config['tests']['connection_test']
        timeout = connection_config.get('connection_timeout', 2.0)
        
        try:
            ws = await asyncio.wait_for(
                websockets.connect(f"{self.ws_url}?id={user_id}"),
                timeout=timeout
            )
            return ws
        except Exception:
            return None
    
    async def run_connection_test(self):
        """Configurable connection test"""
        if not self.config['tests']['connection_test']['enabled']:
            print("⏭️ Connection test disabled")
            return None
            
        conn_config = self.config['tests']['connection_test']
        target = conn_config['target_connections']
        batch_size = conn_config['batch_size']
        failure_threshold = conn_config['failure_threshold']
        
        print(f"\n🌊 CONNECTION TEST")
        print("=" * 50)
        print(f"🎯 Target: {target:,} connections")
        print(f"📦 Batch size: {batch_size}")
        
        successful = 0
        failed = 0
        start_time = time.time()
        
        progress_interval = self.config['reporting']['progress_interval']
        
        for batch_start in range(0, target, batch_size):
            batch_end = min(batch_start + batch_size, target)
            
            # Create batch
            tasks = []
            for i in range(batch_start, batch_end):
                tasks.append(self.create_single_connection(f"user_{i}"))
                
            try:
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in batch_results:
                    if result and not isinstance(result, Exception):
                        self.connections.append(result)
                        successful += 1
                    else:
                        failed += 1
                        
            except Exception as e:
                print(f"❌ Batch {batch_start}-{batch_end} failed: {e}")
                failed += (batch_end - batch_start)
                break
            
            # Progress reporting
            if batch_start % progress_interval == 0 or successful >= target * 0.8:
                current_rate = successful / (time.time() - start_time)
                print(f"📊 Progress: {successful:,}/{batch_end:,} connections ({current_rate:.1f} conn/sec)")
            
            # Failure threshold check
            if batch_end > 1000 and successful < batch_end * failure_threshold:
                print(f"⚠️ High failure rate, stopping at {successful:,} connections")
                break
                
            await asyncio.sleep(0.05)
        
        total_time = time.time() - start_time
        success_rate = (successful / target) * 100
        
        result = {
            'test': 'configurable_connection_test',
            'config': conn_config,
            'target_connections': target,
            'successful_connections': successful,
            'failed_connections': failed,
            'success_rate': success_rate,
            'creation_time': total_time,
            'connection_rate': successful / total_time if total_time > 0 else 0,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        print(f"📊 CONNECTION RESULTS:")
        print(f"   ✅ Achieved: {successful:,}/{target:,} ({success_rate:.1f}%)")
        print(f"   ⚡ Rate: {result['connection_rate']:.1f} conn/sec")
        print(f"   ⏱️ Time: {total_time:.2f}s")
        
        self.session_data['test_results'].append(result)
        return result
    
    async def run_message_test(self):
        """Configurable message test"""
        if not self.config['tests']['message_test']['enabled']:
            print("⏭️ Message test disabled")
            return None
            
        if not self.connections:
            print("❌ No connections available for message test")
            return None
            
        msg_config = self.config['tests']['message_test']
        multiplier = msg_config['target_multiplier']
        batch_size = msg_config['batch_size']
        size_multiplier = msg_config['message_size_multiplier']
        error_threshold = msg_config['error_threshold']
        
        target_messages = len(self.connections) * multiplier
        
        print(f"\n🌊 MESSAGE TEST")
        print("=" * 50)
        print(f"🎯 Target: {target_messages:,} messages")
        print(f"📦 Batch size: {batch_size}")
        print(f"💪 Using: {len(self.connections):,} connections")
        
        start_time = time.time()
        messages_sent = 0
        errors = 0
        
        progress_interval = self.config['reporting']['progress_interval']
        
        for i in range(0, target_messages, batch_size):
            batch_end = min(i + batch_size, target_messages)
            batch_tasks = []
            
            for j in range(i, batch_end):
                ws = self.connections[j % len(self.connections)]
                message = {
                    "type": "configurable_test",
                    "content": f"MSG_{j}_📊" * size_multiplier,
                    "sequence": j
                }
                
                async def send_message(ws, msg):
                    try:
                        await ws.send(json.dumps(msg))
                        return True
                    except:
                        return False
                
                batch_tasks.append(send_message(ws, message))
            
            try:
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                batch_sent = sum(1 for r in batch_results if r is True)
                batch_errors = len(batch_results) - batch_sent
                
                messages_sent += batch_sent
                errors += batch_errors
                
                # Progress reporting
                if i % progress_interval == 0 and i > 0:
                    current_rate = messages_sent / (time.time() - start_time)
                    print(f"📊 Progress: {messages_sent:,}/{target_messages:,} ({current_rate:.0f} msg/sec)")
                
                # Error threshold check
                if errors > error_threshold:
                    print(f"⚠️ Too many errors ({errors}), stopping test")
                    break
                    
            except Exception as e:
                print(f"❌ Batch failed: {e}")
                errors += (batch_end - i)
                break
        
        total_time = time.time() - start_time
        success_rate = (messages_sent / target_messages) * 100
        message_rate = messages_sent / total_time if total_time > 0 else 0
        
        result = {
            'test': 'configurable_message_test',
            'config': msg_config,
            'target_messages': target_messages,
            'messages_sent': messages_sent,
            'errors': errors,
            'success_rate': success_rate,
            'message_rate': message_rate,
            'test_time': total_time,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        print(f"📊 MESSAGE RESULTS:")
        print(f"   ✅ Sent: {messages_sent:,}/{target_messages:,} ({success_rate:.1f}%)")
        print(f"   ⚡ Rate: {message_rate:,.0f} msg/sec")
        print(f"   ❌ Errors: {errors}")
        print(f"   ⏱️ Time: {total_time:.2f}s")
        
        self.session_data['test_results'].append(result)
        return result
    
    async def run_endurance_test(self):
        """Configurable endurance test"""
        if not self.config['tests']['endurance_test']['enabled']:
            print("⏭️ Endurance test disabled")
            return None
            
        if not self.connections:
            print("❌ No connections available for endurance test")
            return None
            
        endurance_config = self.config['tests']['endurance_test']
        duration = endurance_config['duration']
        checkpoint_interval = endurance_config['checkpoint_interval']
        messages_per_batch = endurance_config['messages_per_batch']
        
        print(f"\n💪 ENDURANCE TEST")
        print("=" * 50)
        print(f"🎯 Duration: {duration} seconds")
        print(f"📊 Checkpoint interval: {checkpoint_interval}s")
        
        start_time = time.time()
        total_messages = 0
        
        while time.time() - start_time < duration:
            checkpoint_start = time.time()
            checkpoint_messages = 0
            
            while time.time() - checkpoint_start < checkpoint_interval:
                tasks = []
                
                for i in range(messages_per_batch):
                    ws = self.connections[i % len(self.connections)]
                    message = {
                        "type": "endurance_test",
                        "content": f"ENDURANCE_{total_messages + i}",
                        "timestamp": time.time()
                    }
                    
                    async def quick_send(ws, msg):
                        try:
                            await ws.send(json.dumps(msg))
                            return True
                        except:
                            return False
                    
                    tasks.append(quick_send(ws, message))
                
                try:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    sent = sum(1 for r in results if r is True)
                    checkpoint_messages += sent
                    total_messages += sent
                except:
                    pass
            
            elapsed = time.time() - start_time
            current_rate = checkpoint_messages / checkpoint_interval
            avg_rate = total_messages / elapsed
            
            print(f"💪 ENDURANCE [{elapsed:.0f}s]: {checkpoint_messages:,} msgs ({current_rate:.0f}/sec, avg: {avg_rate:.0f}/sec)")
        
        total_time = time.time() - start_time
        final_rate = total_messages / total_time
        
        result = {
            'test': 'configurable_endurance_test',
            'config': endurance_config,
            'duration': total_time,
            'total_messages': total_messages,
            'average_rate': final_rate,
            'connections_used': len(self.connections),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        print(f"💪 ENDURANCE RESULTS:")
        print(f"   ⏱️ Duration: {total_time:.1f}s")
        print(f"   📊 Messages: {total_messages:,}")
        print(f"   🚀 Avg Rate: {final_rate:.0f} msg/sec")
        
        self.session_data['test_results'].append(result)
        return result
    
    def save_results(self):
        """Save all results"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Calculate summary
        max_connections = 0
        max_message_rate = 0
        total_messages = 0
        
        for result in self.session_data['test_results']:
            if 'connection' in result['test']:
                max_connections = max(max_connections, result.get('successful_connections', 0))
            if 'message' in result['test']:
                max_message_rate = max(max_message_rate, result.get('message_rate', 0))
                total_messages += result.get('messages_sent', 0)
        
        self.session_data['summary'] = {
            'max_connections': max_connections,
            'peak_message_rate': max_message_rate,
            'total_messages': total_messages,
            'test_config': self.config['test_name']
        }
        
        # Save JSON
        json_file = self.results_dir / f"results_{self.session_id}.json"
        with open(json_file, 'w') as f:
            json.dump(self.session_data, f, indent=2)
        
        print(f"💾 [{timestamp}] Results saved: {json_file}")
        
        # Create markdown report
        self.create_report()
        
    def create_report(self):
        """Create markdown report"""
        summary = self.session_data['summary']
        
        report = f"""# {self.config['test_name'].replace('_', ' ').title()} Results

## Test Configuration: {self.config['test_name']}
**Description:** {self.config['description']}
**Session:** {self.session_id}
**Date:** {datetime.now().strftime("%B %d, %Y at %H:%M:%S")}

## 🏆 Summary Results
- **Max Connections:** {summary['max_connections']:,}
- **Peak Message Rate:** {summary['peak_message_rate']:,.0f} msg/sec  
- **Total Messages:** {summary['total_messages']:,}

## 📊 Detailed Results

"""
        
        for result in self.session_data['test_results']:
            test_name = result['test'].replace('_', ' ').title()
            report += f"### {test_name}\n\n"
            
            if 'connection' in result['test']:
                report += f"""- **Target:** {result.get('target_connections', 0):,}
- **Achieved:** {result.get('successful_connections', 0):,}
- **Success Rate:** {result.get('success_rate', 0):.1f}%
- **Rate:** {result.get('connection_rate', 0):.1f} conn/sec

"""
            elif 'message' in result['test']:
                report += f"""- **Target:** {result.get('target_messages', 0):,}
- **Sent:** {result.get('messages_sent', 0):,}
- **Success Rate:** {result.get('success_rate', 0):.1f}%
- **Rate:** {result.get('message_rate', 0):,.0f} msg/sec
- **Errors:** {result.get('errors', 0)}

"""
            elif 'endurance' in result['test']:
                report += f"""- **Duration:** {result.get('duration', 0):.1f}s
- **Messages:** {result.get('total_messages', 0):,}
- **Average Rate:** {result.get('average_rate', 0):,.0f} msg/sec

"""
        
        report_file = self.results_dir / f"report_{self.session_id}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"📝 Report saved: {report_file}")
    
    async def run_benchmark_suite(self):
        """Run the complete configurable benchmark suite"""
        print(f"🔥 CONFIGURABLE BENCHMARK SUITE")
        print("=" * 60)
        print(f"📋 Config: {self.config['test_name']}")
        print(f"📝 {self.config['description']}")
        print("=" * 60)
        
        try:
            # Start server
            if not await self.start_server():
                return
            
            # Run enabled tests
            await self.run_connection_test()
            await asyncio.sleep(3)
            
            await self.run_message_test()
            await asyncio.sleep(3)
            
            await self.run_endurance_test()
            
        finally:
            # Cleanup
            print(f"\n🧹 Cleaning up {len(self.connections):,} connections...")
            for ws in self.connections:
                try:
                    await ws.close()
                except:
                    pass
            
            self.stop_server()
            self.save_results()
            
            print(f"\n🎉 BENCHMARK COMPLETE!")
            print(f"📁 Results: {self.results_dir}")

async def main():
    parser = argparse.ArgumentParser(description='Universal Benchmark Suite')
    parser.add_argument('config', help='Configuration file path')
    parser.add_argument('--list-configs', action='store_true', help='List available configs')
    
    args = parser.parse_args()
    
    if args.list_configs:
        print("📁 Available configurations:")
        config_dir = Path("benchmark-configs")
        if config_dir.exists():
            for config_file in config_dir.glob("*.json"):
                print(f"   📄 {config_file.name}")
        return
    
    if not Path(args.config).exists():
        print(f"❌ Config file not found: {args.config}")
        return
    
    benchmark = UniversalBenchmarkSuite(args.config)
    await benchmark.run_benchmark_suite()

if __name__ == "__main__":
    asyncio.run(main())
