defmodule ElixirChat.ChatServer do
  @moduledoc """
  High-performance chat server using GenServer with ETS optimization
  """
  use GenServer
  require Logger

  # ETS tables for maximum speed
  @connections_table :chat_connections
  @stats_table :chat_stats

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{}, name: __MODULE__)
  end

  def init(_) do
    # Create ETS tables for blazing fast lookups
    :ets.new(@connections_table, [:set, :public, :named_table, {:read_concurrency, true}])
    :ets.new(@stats_table, [:set, :public, :named_table, {:write_concurrency, true}])
    
    # Initialize stats
    :ets.insert(@stats_table, {:connections, 0})
    :ets.insert(@stats_table, {:messages, 0})
    :ets.insert(@stats_table, {:start_time, System.system_time(:millisecond)})
    
    Logger.info("🚀 ElixirChat server started with ETS optimization")
    {:ok, %{}}
  end

  # Lightning-fast connection management
  def add_connection(user_id, pid) do
    :ets.insert(@connections_table, {user_id, pid})
    count = :ets.update_counter(@stats_table, :connections, 1)
    
    if rem(count, 1000) == 0 do
      Logger.info("📊 Connections: #{count}")
    end
    
    :ok
  end

  def remove_connection(user_id) do
    :ets.delete(@connections_table, user_id)
    :ets.update_counter(@stats_table, :connections, -1)
    :ok
  end

  def broadcast_message(message) do
    # Batch broadcast for efficiency
    :ets.update_counter(@stats_table, :messages, 1)
    
    # Get all connections in one ETS scan
    connections = :ets.tab2list(@connections_table)
    
    # Parallel broadcast using Task.async_stream for maximum throughput
    connections
    |> Task.async_stream(
      fn {_user_id, pid} ->
        send(pid, {:broadcast, message})
      end,
      max_concurrency: System.schedulers_online() * 4,
      timeout: 100
    )
    |> Stream.run()
    
    :ok
  end

  def get_stats do
    [{:connections, conn_count}] = :ets.lookup(@stats_table, :connections)
    [{:messages, msg_count}] = :ets.lookup(@stats_table, :messages)
    [{:start_time, start_time}] = :ets.lookup(@stats_table, :start_time)
    
    uptime = System.system_time(:millisecond) - start_time
    
    %{
      connections: conn_count,
      messages: msg_count,
      uptime_ms: uptime,
      message_rate: if(uptime > 0, do: msg_count * 1000 / uptime, else: 0)
    }
  end
end
