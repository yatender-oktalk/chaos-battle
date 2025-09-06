# Connect to running node and check ETS stats
:timer.sleep(1000)  # Wait a second

loop_check = fn ->
  conn_info = try do
    :ets.info(:connections)
  rescue
    _ -> :not_found
  end
  
  stats_info = try do
    :ets.info(:stats)
  rescue  
    _ -> :not_found
  end

  IO.puts("=== ETS Status ===")
  IO.puts("Connections table: #{inspect(conn_info)}")
  IO.puts("Stats table: #{inspect(stats_info)}")
  
  if conn_info != :not_found do
    IO.puts("Connection count: #{conn_info[:size]}")
    IO.puts("Memory used: #{conn_info[:memory]} words")
  end
  
  # Check total ETS memory
  total_ets = :ets.all() |> length()
  IO.puts("Total ETS tables: #{total_ets}")
  IO.puts("========================")
end

# Run check every 2 seconds for 30 seconds
for _ <- 1..15 do
  loop_check.()
  :timer.sleep(2000)
end
