defmodule ElixirChatWeb.ChatChannel do
  use Phoenix.Channel
  require Logger
  alias ElixirChat.ChatServer

  def join("chat:lobby", _params, socket) do
    user_id = socket.assigns.user_id
    
    # Register with chat server
    ChatServer.add_connection(user_id, self())
    
    # Monitor for cleanup
    Process.monitor(self())
    
    {:ok, %{user_id: user_id}, socket}
  end

  def handle_in("message", %{"content" => content}, socket) do
    user_id = socket.assigns.user_id
    
    message = %{
      user_id: user_id,
      content: content,
      timestamp: System.system_time(:millisecond),
      type: "message"
    }
    
    # Broadcast to all connections
    ChatServer.broadcast_message(message)
    
    {:noreply, socket}
  end

  def handle_in("ping", _params, socket) do
    push(socket, "pong", %{timestamp: System.system_time(:millisecond)})
    {:noreply, socket}
  end

  def handle_in("benchmark_test", params, socket) do
    # Handle benchmark messages efficiently
    message = %{
      type: "benchmark",
      content: params["content"] || "benchmark_message",
      sequence: params["sequence"] || 0,
      user_id: socket.assigns.user_id,
      timestamp: System.system_time(:millisecond)
    }
    
    ChatServer.broadcast_message(message)
    {:noreply, socket}
  end

  def handle_info({:broadcast, message}, socket) do
    push(socket, "message", message)
    {:noreply, socket}
  end

  def handle_info({:DOWN, _ref, :process, _pid, _reason}, socket) do
    ChatServer.remove_connection(socket.assigns.user_id)
    {:noreply, socket}
  end

  def terminate(_reason, socket) do
    ChatServer.remove_connection(socket.assigns.user_id)
    :ok
  end
end
