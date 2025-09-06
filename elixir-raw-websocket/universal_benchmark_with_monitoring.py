# Save as universal-benchmark-with-monitoring.py
import asyncio
import websockets
import json
import time
import psutil
import threading
import sys
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import os

@dataclass
class SystemSnapshot:
    timestamp: float
    cpu_percent: float
    memory_used_mb: float
    memory_percent: float
    beam_cpu_percent: float
    beam_memory_mb: float
    beam_memory_percent: float
    connections_count: int
    open_files: int
    network_connections: int

class SystemMonitor:
    def __init__(self):
        self.snapshots: List[SystemSnapshot] = []
        self.monitoring = False
        self.beam_process = None
        self.monitor_thread = None
        
    def find_beam_process(self):
        """Find the BEAM/Elixir process"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'beam.smp' in proc.info['name'] or 'beam' in proc.info['name']:
                    if 'elixir' in ' '.join(proc.info['cmdline']).lower():
                        return psutil.Process(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def start_monitoring(self):
        """Start system monitoring in background thread"""
        self.beam_process = self.find_beam_process()
        if not self.beam_process:
            print("⚠️  Could not find BEAM process - monitoring system only")
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("🔍 System monitoring started...")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("🔍 System monitoring stopped...")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # System metrics
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                
                # BEAM process metrics
                beam_cpu = 0.0
                beam_memory_mb = 0.0
                beam_memory_percent = 0.0
                open_files = 0
                network_connections = 0
                
                if self.beam_process and self.beam_process.is_running():
                    try:
                        beam_cpu = self.beam_process.cpu_percent()
                        beam_memory_info = self.beam_process.memory_info()
                        beam_memory_mb = beam_memory_info.rss / 1024 / 1024
                        beam_memory_percent = self.beam_process.memory_percent()
                        
                        # Count open files
                        try:
                            open_files = len(self.beam_process.open_files())
                        except (psutil.AccessDenied, psutil.NoSuchProcess):
                            open_files = 0
                        
                        # Count network connections
                        try:
                            connections = self.beam_process.connections()
                            network_connections = len([c for c in connections if c.laddr.port == 8081])
                        except (psutil.AccessDenied, psutil.NoSuchProcess):
                            network_connections = 0
                            
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        self.beam_process = self.find_beam_process()
                
                snapshot = SystemSnapshot(
                    timestamp=time.time(),
                    cpu_percent=cpu_percent,
                    memory_used_mb=memory.used / 1024 / 1024,
                    memory_percent=memory.percent,
                    beam_cpu_percent=beam_cpu,
                    beam_memory_mb=beam_memory_mb,
                    beam_memory_percent=beam_memory_percent,
                    connections_count=0,  # Will be updated during tests
                    open_files=open_files,
                    network_connections=network_connections
                )
                
                self.snapshots.append(snapshot)
                
                # Keep only last 10 minutes of data
                cutoff_time = time.time() - 600
                self.snapshots = [s for s in self.snapshots if s.timestamp > cutoff_time]
                
            except Exception as e:
                print(f"⚠️  Monitoring error: {e}")
            
            time.sleep(1)  # Monitor every second
    
    def get_current_stats(self) -> Optional[SystemSnapshot]:
        """Get the most recent snapshot"""
        return self.snapshots[-1] if self.snapshots else None
    
    def get_stats_summary(self) -> Dict:
        """Get summary statistics"""
        if not self.snapshots:
            return {}
        
        cpu_values = [s.cpu_percent for s in self.snapshots]
        memory_values = [s.memory_used_mb for s in self.snapshots]
        beam_cpu_values = [s.beam_cpu_percent for s in self.snapshots]
        beam_memory_values = [s.beam_memory_mb for s in self.snapshots]
        
        return {
            "monitoring_duration": self.snapshots[-1].timestamp - self.snapshots[0].timestamp,
            "total_snapshots": len(self.snapshots),
            "system_cpu": {
                "min": min(cpu_values),
                "max": max(cpu_values),
                "avg": sum(cpu_values) / len(cpu_values)
            },
            "system_memory": {
                "min_mb": min(memory_values),
                "max_mb": max(memory_values),
                "avg_mb": sum(memory_values) / len(memory_values)
            },
            "beam_cpu": {
                "min": min(beam_cpu_values) if beam_cpu_values else 0,
                "max": max(beam_cpu_values) if beam_cpu_values else 0,
                "avg": sum(beam_cpu_values) / len(beam_cpu_values) if beam_cpu_values else 0
            },
            "beam_memory": {
                "min_mb": min(beam_memory_values) if beam_memory_values else 0,
                "max_mb": max(beam_memory_values) if beam_memory_values else 0,
                "avg_mb": sum(beam_memory_values) / len(beam_memory_values) if beam_memory_values else 0
            },
            "peak_open_files": max([s.open_files for s in self.snapshots]),
            "peak_network_connections": max([s.network_connections for s in self.snapshots])
        }

# Enhanced benchmark class
class EnhancedWebSocketBenchmark:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.server_url = self.config["server_url"]
        self.test_name = self.config.get("test_name", "websocket_test")
        self.monitor = SystemMonitor()
        self.connections = []
        
    async def test_connections(self):
        """Enhanced connection test with monitoring"""
        test_config = self.config["tests"]["connection_test"]
        if not test_config.get("enabled", True):
            return None
            
        target = test_config["target_connections"]
        batch_size = test_config["batch_size"]
        timeout = test_config["connection_timeout"]
        
        print(f"\n🔥 ENHANCED CONNECTION TEST WITH MONITORING")
        print("=" * 60)
        print(f"🎯 Target: {target:,} connections")
        print(f"📦 Batch size: {batch_size}")
        print(f"⏱️ Timeout: {timeout}s")
        
        successful = 0
        failed = 0
        start_time = time.time()
        
        # Start monitoring
        self.monitor.start_monitoring()
        
        try:
            for i in range(0, target, batch_size):
                batch_start = time.time()
                batch_tasks = []
                
                current_batch_size = min(batch_size, target - i)
                
                for _ in range(current_batch_size):
                    task = asyncio.create_task(self._connect_with_timeout(timeout))
                    batch_tasks.append(task)
                
                # Wait for batch to complete
                results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # Count results
                for result in results:
                    if isinstance(result, Exception):
                        failed += 1
                    else:
                        successful += 1
                        if result:
                            self.connections.append(result)
                
                # Update monitoring with current connection count
                if self.monitor.snapshots:
                    self.monitor.snapshots[-1].connections_count = successful
                
                # Progress update with system stats
                if i % (batch_size * 10) == 0 and i > 0:
                    elapsed = time.time() - start_time
                    rate = successful / elapsed
                    current_stats = self.monitor.get_current_stats()
                    
                    if current_stats:
                        print(f"📊 Progress: {successful:,}/{target:,} ({successful/target*100:.1f}%) | "
                              f"Rate: {rate:.1f}/sec | "
                              f"CPU: {current_stats.cpu_percent:.1f}% | "
                              f"BEAM RAM: {current_stats.beam_memory_mb:.1f}MB | "
                              f"BEAM CPU: {current_stats.beam_cpu_percent:.1f}%")
                    else:
                        print(f"📊 Progress: {successful:,}/{target:,} ({successful/target*100:.1f}%) | Rate: {rate:.1f}/sec")
        
        except KeyboardInterrupt:
            print("\n⚠️ Test interrupted by user")
        
        # Final stats
        duration = time.time() - start_time
        final_stats = self.monitor.get_current_stats()
        
        print(f"\n📊 ENHANCED CONNECTION RESULTS:")
        print(f"   ✅ Achieved: {successful:,}/{target:,} ({successful/target*100:.1f}%)")
        print(f"   ⚡ Rate: {successful/duration:.1f} conn/sec")
        print(f"   ⏱️ Time: {duration:.2f}s")
        print(f"   ❌ Failed: {failed:,}")
        
        if final_stats:
            print(f"   💾 Final BEAM RAM: {final_stats.beam_memory_mb:.1f}MB")
            print(f"   🖥️ Final BEAM CPU: {final_stats.beam_cpu_percent:.1f}%")
            print(f"   📁 Open Files: {final_stats.open_files:,}")
            print(f"   🌐 Network Connections: {final_stats.network_connections:,}")
        
        return {
            "target_connections": target,
            "successful_connections": successful,
            "failed_connections": failed,
            "success_rate": (successful / target) * 100,
            "connection_rate": successful / duration,
            "duration": duration,
            "batch_size": batch_size,
            "timeout": timeout,
            "final_system_stats": asdict(final_stats) if final_stats else None
        }
    
    async def _connect_with_timeout(self, timeout):
        """Connect with timeout"""
        try:
            ws = await asyncio.wait_for(
                websockets.connect(
                    self.server_url,
                    ping_interval=None,
                    close_timeout=1,
                    open_timeout=timeout
                ),
                timeout=timeout
            )
            return ws
        except Exception:
            return None
    
    async def run_benchmark(self):
        """Run the enhanced benchmark"""
        print(f"🚀 ENHANCED WEBSOCKET BENCHMARK WITH SYSTEM MONITORING")
        print(f"Server: {self.server_url}")
        print(f"Test: {self.test_name}")
        print(f"Time: {datetime.now().isoformat()}")
        
        results = {
            "benchmark_info": {
                "test_name": self.test_name,
                "timestamp": datetime.now().isoformat(),
                "server_url": self.server_url
            }
        }
        
        # Run connection test
        if self.config["tests"].get("connection_test", {}).get("enabled", True):
            connection_results = await self.test_connections()
            if connection_results:
                results["connection_test"] = connection_results
        
        # Get monitoring summary
        monitoring_summary = self.monitor.get_stats_summary()
        if monitoring_summary:
            results["system_monitoring"] = monitoring_summary
            results["monitoring_snapshots"] = [asdict(s) for s in self.monitor.snapshots]
        
        # Stop monitoring
        self.monitor.stop_monitoring()
        
        # Cleanup connections
        if self.connections:
            print(f"\n🧹 Cleaning up {len(self.connections):,} connections...")
            for ws in self.connections:
                try:
                    await ws.close()
                except:
                    pass
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"results/enhanced_benchmark_{self.test_name}_{timestamp}.json"
        
        os.makedirs("results", exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {results_file}")
        return results

async def main():
    if len(sys.argv) != 2:
        print("Usage: python universal-benchmark-with-monitoring.py <config.json>")
        sys.exit(1)
    
    config_path = sys.argv[1]
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)
    
    benchmark = EnhancedWebSocketBenchmark(config_path)
    results = await benchmark.run_benchmark()
    
    # Print summary
    print(f"\n🏆 ENHANCED BENCHMARK COMPLETE")
    print("=" * 50)
    
    if "connection_test" in results:
        ct = results["connection_test"]
        print(f"🔗 Connections: {ct['successful_connections']:,}/{ct['target_connections']:,} ({ct['success_rate']:.1f}%)")
        print(f"⚡ Rate: {ct['connection_rate']:.1f} conn/sec")
    
    if "system_monitoring" in results:
        sm = results["system_monitoring"]
        print(f"📊 Monitoring: {sm['total_snapshots']} snapshots over {sm['monitoring_duration']:.1f}s")
        print(f"🖥️ System CPU: {sm['system_cpu']['avg']:.1f}% avg, {sm['system_cpu']['max']:.1f}% peak")
        print(f"💾 BEAM Memory: {sm['beam_memory']['avg_mb']:.1f}MB avg, {sm['beam_memory']['max_mb']:.1f}MB peak")
        print(f"⚡ BEAM CPU: {sm['beam_cpu']['avg']:.1f}% avg, {sm['beam_cpu']['max']:.1f}% peak")

if __name__ == "__main__":
    asyncio.run(main())