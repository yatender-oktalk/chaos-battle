# Live connection monitoring with failure detection

defmodule ConnectionMonitor do
  def start_monitoring() do
    IO.puts("🔍 STARTING REAL-TIME CONNECTION MONITOR")
    IO.puts("======================================")
    
    spawn(fn -> monitor_loop(0, 0, System.monotonic_time(:millisecond)) end)
  end
  
  defp monitor_loop(last_count, last_failed, start_time) do
    current_time = System.monotonic_time(:millisecond)
    
    # Get current stats
    current_count = case :ets.lookup(:stats, :connections) do
      [{:connections, count}] -> count
      [] -> 0
    end
    
    # Check for failed connection attempts (if we're tracking them)
    current_failed = case :ets.lookup(:stats, :failed_connections) do
      [{:failed_connections, failed}] -> failed
      [] -> 0
    end
    
    # Calculate rates
    time_diff = current_time - start_time
    rate = if time_diff > 0, do: current_count * 1000 / time_diff, else: 0
    
    # Check for problems
    connection_delta = current_count - last_count
    failed_delta = current_failed - last_failed
    
    status = cond do
      connection_delta < 0 -> "⚠️  DROPPING"
      connection_delta == 0 and current_count < 40000 -> "⏸️  STALLED"
      failed_delta > 100 -> "❌ HIGH FAILURES"
      true -> "✅ HEALTHY"
    end
    
    IO.puts("#{status} | Connections: #{current_count} | Rate: #{:erlang.float_to_binary(rate, decimals: 1)}/sec | Failed: #{current_failed}")
    
    # Check system resources every 10 iterations
    if rem(:erlang.system_time(:second), 10) == 0 do
      check_system_resources()
    end
    
    :timer.sleep(1000)
    monitor_loop(current_count, current_failed, start_time)
  end
  
  defp check_system_resources() do
    # Check memory
    memory = :erlang.memory()
    total_mb = div(memory[:total], 1024 * 1024)
    
    # Check process count
    process_count = :erlang.system_info(:process_count)
    process_limit = :erlang.system_info(:process_limit)
    
    if total_mb > 8000 do
      IO.puts("⚠️  HIGH MEMORY: #{total_mb}MB")
    end
    
    if process_count > process_limit * 0.8 do
      IO.puts("⚠️  HIGH PROCESS COUNT: #{process_count}/#{process_limit}")
    end
  end
end

# Add failure tracking to your ETS tables
:ets.new(:stats, [:set, :public, :named_table])
:ets.insert(:stats, {:connections, 0})
:ets.insert(:stats, {:failed_connections, 0})

ConnectionMonitor.start_monitoring()
