defmodule ElixirRawChat.HealthHandler do
  def init(req, state) do
    body =
      Jason.encode!(%{
        status: "ok",
        server: "raw_elixir_websocket",
        timestamp: System.system_time(:millisecond)
      })

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
