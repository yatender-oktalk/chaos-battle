# Live monitoring to catch the exact moment connections stop growing

defmodule LiveMonitor do
  def start() do
    IO.puts("🔍 LIVE CONNECTION MONITOR - Finding the bottleneck!")
    IO.puts("===================================================")
    
    # Ensure ETS tables exist
    unless :ets.whereis(:connections) do
      :ets.new(:connections, [:set, :public, :named_table])
    end
    unless :ets.whereis(:stats) do
      :ets.new(:stats, [:set, :public, :named_table])
      :ets.insert(:stats, {:connections, 0})
    end
    
    monitor_loop(0, System.monotonic_time(:millisecond))
  end
  
  defp monitor_loop(last_count, start_time) do
    current_time = System.monotonic_time(:millisecond)
    
    # Get current connection count
    current_count = case :ets.lookup(:stats, :connections) do
      [{:connections, count}] -> count
      [] -> 0
    end
    
    # Calculate metrics
    time_elapsed = (current_time - start_time) / 1000
    rate = if time_elapsed > 0, do: current_count / time_elapsed, else: 0
    delta = current_count - last_count
    
    # System info
    memory = :erlang.memory()
    total_mb = div(memory[:total], 1024 * 1024)
    process_count = :erlang.system_info(:process_count)
    
    # Status determination
    status = cond do
      current_count == 0 -> "⏳ WAITING"
      delta > 100 -> "🚀 FAST GROWTH"
      delta > 10 -> "📈 GROWING"
      delta > 0 -> "🐌 SLOW GROWTH"
      delta == 0 and current_count > 0 -> "⏸️ STALLED"
      delta < 0 -> "📉 DROPPING"
      true -> "❓ UNKNOWN"
    end
    
    IO.puts("#{format_time(time_elapsed)} | #{status} | Conn: #{format_number(current_count)} | Δ#{delta} | Rate: #{:erlang.float_to_binary(rate, decimals: 1)}/s | Mem: #{total_mb}MB | Proc: #{process_count}")
    
    # Alert on potential issues
    cond do
      current_count > 20000 and delta == 0 ->
        IO.puts("�� BOTTLENECK DETECTED at #{current_count} connections!")
        analyze_bottleneck()
      total_mb > 2000 ->
        IO.puts("⚠️ HIGH MEMORY: #{total_mb}MB")
      process_count > 100000 ->
        IO.puts("⚠️ HIGH PROCESS COUNT: #{process_count}")
      true -> :ok
    end
    
    :timer.sleep(1000)
    monitor_loop(current_count, start_time)
  end
  
  defp analyze_bottleneck() do
    IO.puts("\n🔍 BOTTLENECK ANALYSIS:")
    
    # Check system limits
    limits = [
      {:process_limit, :erlang.system_info(:process_limit)},
      {:process_count, :erlang.system_info(:process_count)},
      {:port_limit, :erlang.system_info(:port_limit)},
      {:port_count, :erlang.system_info(:port_count)}
    ]
    
    Enum.each(limits, fn {name, value} ->
      IO.puts("  #{name}: #{value}")
    end)
    
    # Check ETS table size
    ets_size = :ets.info(:connections, :size)
    IO.puts("  ETS connections size: #{ets_size}")
    
    IO.puts("")
  end
  
  defp format_time(seconds) when seconds < 60 do
    "#{:erlang.float_to_binary(seconds, decimals: 1)}s"
  end
  
  defp format_time(seconds) do
    minutes = div(trunc(seconds), 60)
    remaining = seconds - (minutes * 60)
    "#{minutes}m#{:erlang.float_to_binary(remaining, decimals: 1)}s"
  end
  
  defp format_number(num) when num >= 1000 do
    "#{div(num, 1000)}k"
  end
  
  defp format_number(num), do: "#{num}"
end

LiveMonitor.start()
