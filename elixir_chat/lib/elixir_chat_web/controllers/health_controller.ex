defmodule ElixirChatWeb.HealthController do
  use ElixirChatWeb, :controller
  alias ElixirChat.ChatServer

  def index(conn, _params) do
    json(conn, %{status: "ok", timestamp: System.system_time(:millisecond)})
  end

  def stats(conn, _params) do
    stats = ChatServer.get_stats()
    json(conn, stats)
  end

  def metrics(conn, _params) do
    stats = ChatServer.get_stats()
    
    metrics = %{
      connections_current: stats.connections,
      messages_total: stats.messages,
      uptime_seconds: div(stats.uptime_ms, 1000),
      message_rate_per_second: round(stats.message_rate),
      memory_usage: :erlang.memory(),
      process_count: :erlang.system_info(:process_count),
      scheduler_utilization: :scheduler.utilization(1)
    }
    
    json(conn, metrics)
  end
end
