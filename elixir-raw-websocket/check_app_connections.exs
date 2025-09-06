# Check our application's connection tracking
try do
  # Check ETS tables
  connections = :ets.tab2list(:connections)
  stats = :ets.tab2list(:stats)
  
  IO.puts("=== APPLICATION STATE ===")
  IO.puts("Active connections: #{length(connections)}")
  IO.puts("Stats entries: #{length(stats)}")
  
  # Check ETS table info
  conn_info = :ets.info(:connections)
  IO.puts("Connections table memory: #{conn_info[:memory]} words")
  IO.puts("Connections table size: #{conn_info[:size]}")
  
  # Sample a few connections
  sample_connections = connections |> Enum.take(5)
  IO.puts("Sample connections: #{inspect(sample_connections)}")
  
rescue
  e -> IO.puts("Error checking app state: #{inspect(e)}")
end
