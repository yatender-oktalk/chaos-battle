defmodule ElixirRawChat.StatsHandler do
  def init(req, state) do
    # Get live stats from ETS
    connections =
      case :ets.lookup(:stats, :connections) do
        [{:connections, count}] -> count
        [] -> 0
      end

    messages =
      case :ets.lookup(:stats, :messages) do
        [{:messages, count}] -> count
        [] -> 0
      end

    # Get connection details
    all_connections = :ets.tab2list(:connections)

    stats = %{
      connections: connections,
      messages: messages,
      connection_list: length(all_connections),
      timestamp: System.system_time(:millisecond),
      server: "raw_elixir_cowboy",
      uptime: System.monotonic_time() |> System.convert_time_unit(:native, :second)
    }

    body = Jason.encode!(stats)

    req =
      :cowboy_req.reply(
        200,
        %{"content-type" => "application/json"},
        body,
        req
      )

    {:ok, req, state}
  end
end
