# Check Ranch listener info
listener_info = :ranch.info()
IO.puts("Ranch listeners: #{inspect(listener_info)}")

# Check specific listener
raw_info = try do
  :ranch.info(:raw_websocket_server)
rescue
  e -> "Error: #{inspect(e)}"
end

IO.puts("Raw websocket server info: #{inspect(raw_info)}")

# Check connection count
conn_count = try do
  :ranch.procs(:raw_websocket_server, :connections)
rescue
  e -> "Error getting connections: #{inspect(e)}"
end

IO.puts("Active connections: #{inspect(conn_count)}")
