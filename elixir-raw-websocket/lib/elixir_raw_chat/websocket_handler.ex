defmodule ElixirRawChat.WebSocketHandler do
  @moduledoc """
  Raw Cowboy WebSocket handler - MAXIMUM PERFORMANCE
  No Phoenix, no channels, pure WebSocket speed!
  """

  @behaviour :cowboy_websocket

  def init(req, _state) do
    # Extract user ID from path
    user_id = :cowboy_req.binding(:user_id, req, "user_#{:rand.uniform(1_000_000)}")

    # Initialize WebSocket connection
    {:cowboy_websocket, req, %{user_id: user_id, connected_at: System.monotonic_time()}}
  end

  def websocket_init(state) do
    # Register connection in ETS (blazing fast lookup)
    :ets.insert(:connections, {state.user_id, self()})
    result = :ets.update_counter(:stats, :connections, 1, {:connections, 0})
    IO.inspect("Connection count after insert: #{result}")

    # Send welcome message
    welcome = %{
      type: "connected",
      user_id: state.user_id,
      timestamp: System.system_time(:millisecond)
    }

    {:reply, {:text, Jason.encode!(welcome)}, state}
  end

  def websocket_handle({:text, message}, state) do
    # Parse incoming message
    case Jason.decode(message) do
      {:ok, %{"type" => "ping"}} ->
        pong = %{type: "pong", timestamp: System.system_time(:millisecond)}
        {:reply, {:text, Jason.encode!(pong)}, state}

      {:ok, %{"type" => "benchmark_test", "content" => _content, "sequence" => _sequence}} ->
        # Update message counter (ignore unused variables)
        :ets.update_counter(:stats, :messages, 1, {:messages, 0})
        {:ok, state}

      {:ok, %{"type" => "chat_message", "content" => content}} ->
        # Broadcast to all connections
        broadcast_message = %{
          type: "message",
          user_id: state.user_id,
          content: content,
          timestamp: System.system_time(:millisecond)
        }

        broadcast_to_all(Jason.encode!(broadcast_message))
        {:ok, state}

      _ ->
        {:ok, state}
    end
  end

  def websocket_handle({:binary, _data}, state) do
    # Handle binary messages (ultra-fast)
    :ets.update_counter(:stats, :messages, 1, {:messages, 0})
    {:ok, state}
  end

  def websocket_info({:broadcast, message}, state) do
    {:reply, {:text, message}, state}
  end

  def websocket_info(_info, state) do
    {:ok, state}
  end

  def terminate(reason, _req, state) do
    IO.inspect("terminate called for user: #{state.user_id}, reason: #{inspect(reason)}")

    # Clean up connection
    :ets.delete(:connections, state.user_id)
    result = :ets.update_counter(:stats, :connections, -1)
    IO.inspect("Connection count after cleanup: #{result}")
    :ok
  end

  # Ultra-fast broadcast using ETS
  defp broadcast_to_all(message) do
    # Get all connections
    connections = :ets.tab2list(:connections)

    # Send to all connections in parallel
    Enum.each(connections, fn {_user_id, pid} ->
      send(pid, {:broadcast, message})
    end)
  end
end
