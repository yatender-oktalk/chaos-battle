# Monitor BEAM internals during connection test
check_beam = fn ->
  # Process info
  process_count = :erlang.system_info(:process_count)
  process_limit = :erlang.system_info(:process_limit)

  # Port info (file descriptors)
  port_count = :erlang.system_info(:port_count)
  port_limit = :erlang.system_info(:port_limit)

  # Memory
  memory = :erlang.memory()
  total_mb = div(memory[:total], 1024 * 1024)
  processes_mb = div(memory[:processes], 1024 * 1024)

  # ETS info
  ets_count = length(:ets.all())

  # YOUR ACTUAL CONNECTION TRACKING
  connections_count =
    try do
      case :ets.lookup(:stats, :connections) do
        [{:connections, count}] -> count
        [] -> 0
        _ -> 0
      end
    rescue
      _ -> 0
    end

  # Your actual connections table size
  connections_table_size =
    try do
      :ets.info(:connections)[:size] || 0
    rescue
      _ -> 0
    end

  # Message count from your stats
  messages_count =
    try do
      case :ets.lookup(:stats, :messages) do
        [{:messages, count}] -> count
        [] -> 0
        _ -> 0
      end
    rescue
      _ -> 0
    end

  # Ranch connections (if available)
  ranch_connections =
    try do
      ranch_info = :ranch.info()
      total_ranch = Enum.reduce(ranch_info, 0, fn {_name, props}, acc ->
        acc + Keyword.get(props, :all_connections, 0)
      end)
      total_ranch
    rescue
      _ -> 0
    end

  timestamp = DateTime.utc_now() |> DateTime.to_string()

  # Display comprehensive info
  IO.puts("#{timestamp}")
  IO.puts("  📊 BEAM: Processes: #{process_count}/#{process_limit} | Ports: #{port_count}/#{port_limit} | Memory: #{total_mb}MB (proc: #{processes_mb}MB) | ETS: #{ets_count}")
  IO.puts("  🌐 CONNECTIONS: Stats Table: #{connections_count} | ETS Table Size: #{connections_table_size} | Ranch: #{ranch_connections}")
  IO.puts("  📨 MESSAGES: #{messages_count}")

  # Performance indicators
  cond do
    connections_count > 50000 -> IO.puts("  🔥 EXTREME LOAD: #{connections_count} connections!")
    connections_count > 25000 -> IO.puts("  🚀 HIGH LOAD: #{connections_count} connections!")
    connections_count > 10000 -> IO.puts("  ⚡ MEDIUM LOAD: #{connections_count} connections!")
    connections_count > 0 -> IO.puts("  ✅ ACTIVE: #{connections_count} connections")
    true -> IO.puts("  💤 IDLE: No connections")
  end

  IO.puts("")
end

IO.puts("🔍 BEAM Monitor Started for ElixirRawChat - Press Ctrl+C to stop")
IO.puts("=" |> String.duplicate(80))

# Run monitoring loop indefinitely
Stream.repeatedly(fn ->
  check_beam.()
  :timer.sleep(2000)
  :ok
end)
|> Enum.take_while(fn _ -> true end)
