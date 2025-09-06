defmodule SimpleBench do
  @url "http://localhost:8081/health"
  @concurrency 100
  @requests_per_worker 100

  def run do
    IO.puts("Starting benchmark: #{@concurrency} workers, #{@requests_per_worker} requests each")
    start = :os.system_time(:millisecond)

    tasks =
      for _ <- 1..@concurrency do
        Task.async(fn -> worker(@requests_per_worker) end)
      end

    results = Enum.map(tasks, &Task.await(&1, :infinity))
    total = Enum.sum(results)
    duration = :os.system_time(:millisecond) - start

    IO.puts("Total requests: #{total}")
    IO.puts("Total time: #{duration} ms")
    IO.puts("Requests/sec: #{Float.round(total / (duration / 1000), 2)}")
  end

  defp worker(n) do
    Enum.reduce(1..n, 0, fn _, acc ->
      case :httpc.request(:get, {String.to_charlist(@url), []}, [], []) do
        {:ok, _} -> acc + 1
        _ -> acc
      end
    end)
  end
end
defmodule SimpleBench do
  @url "http://localhost:8081/health"
  @concurrency 100
  @requests_per_worker 100

  def run do
    IO.puts("Starting benchmark: #{@concurrency} workers, #{@requests_per_worker} requests each")
    start = :os.system_time(:millisecond)

    tasks =
      for _ <- 1..@concurrency do
        Task.async(fn -> worker(@requests_per_worker) end)
      end

    results = Enum.map(tasks, &Task.await(&1, :infinity))
    total = Enum.sum(results)
    duration = :os.system_time(:millisecond) - start

    IO.puts("Total requests: #{total}")
    IO.puts("Total time: #{duration} ms")
    IO.puts("Requests/sec: #{Float.round(total / (duration / 1000), 2)}")
  end

  defp worker(n) do
    Enum.reduce(1..n, 0, fn _, acc ->
      case :httpc.request(:get, {String.to_charlist(@url), []}, [], []) do
        {:ok, _} -> acc + 1
        _ -> acc
      end
    end)
  end
end

SimpleBench.run()
