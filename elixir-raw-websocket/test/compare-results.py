#!/usr/bin/env python3
import json
import glob
import os
from datetime import datetime

def find_latest_results():
    """Find latest Go and Elixir results"""
    go_results = glob.glob("/Users/ysingh/go/src/github.com/yatender-oktalk/chaos-battle/go-chat/chaos-results/sessions/*/results_*.json")
    elixir_results = glob.glob("/Users/ysingh/go/src/github.com/yatender-oktalk/chaos-battle/elixir-raw-websocket/elixir-raw-websocket/chaos-results/sessions/*/results_*elixir*.json")

    # Get most recent files
    go_latest = max(go_results, key=os.path.getctime) if go_results else None
    elixir_latest = max(elixir_results, key=os.path.getctime) if elixir_results else None

    return go_latest, elixir_latest

def load_results(file_path):
    """Load results from JSON file"""
    if not file_path or not os.path.exists(file_path):
        return None

    with open(file_path, 'r') as f:
        return json.load(f)

def compare_results(go_results, elixir_results):
    """Compare Go vs Elixir results"""
    print("🥊 GO vs ELIXIR BATTLE RESULTS")
    print("=" * 60)

    if go_results and elixir_results:
        # Connection comparison
        go_conn = go_results.get('connection_test', {})
        elixir_conn = elixir_results.get('connection_test', {})

        print(f"\n🔥 CONNECTION BATTLE:")
        print(f"   Go:     {go_conn.get('successful_connections', 0):,} connections ({go_conn.get('success_rate', 0):.1f}%)")
        print(f"   Elixir: {elixir_conn.get('successful_connections', 0):,} connections ({elixir_conn.get('success_rate', 0):.1f}%)")

        go_conns = go_conn.get('successful_connections', 0)
        elixir_conns = elixir_conn.get('successful_connections', 0)

        if go_conns > elixir_conns:
            diff = go_conns - elixir_conns
            print(f"   🥇 GO WINS by {diff:,} connections ({(diff/elixir_conns*100):.1f}% advantage)")
        elif elixir_conns > go_conns:
            diff = elixir_conns - go_conns
            print(f"   🥇 ELIXIR WINS by {diff:,} connections ({(diff/go_conns*100):.1f}% advantage)")
        else:
            print(f"   🤝 TIE!")

        # Message comparison
        go_msg = go_results.get('message_test', {})
        elixir_msg = elixir_results.get('message_test', {})

        print(f"\n⚡ MESSAGE THROUGHPUT BATTLE:")
        print(f"   Go:     {go_msg.get('message_rate', 0):,.0f} msg/sec")
        print(f"   Elixir: {elixir_msg.get('message_rate', 0):,.0f} msg/sec")

        go_rate = go_msg.get('message_rate', 0)
        elixir_rate = elixir_msg.get('message_rate', 0)

        if go_rate > elixir_rate:
            print(f"   🥇 GO WINS ({((go_rate-elixir_rate)/elixir_rate*100):.1f}% faster)")
        elif elixir_rate > go_rate:
            print(f"   🥇 ELIXIR WINS ({((elixir_rate-go_rate)/go_rate*100):.1f}% faster)")
        else:
            print(f"   🤝 TIE!")

        # Endurance comparison
        go_end = go_results.get('endurance_test', {})
        elixir_end = elixir_results.get('endurance_test', {})

        print(f"\n💪 ENDURANCE BATTLE:")
        print(f"   Go:     {go_end.get('average_rate', 0):,.0f} msg/sec sustained")
        print(f"   Elixir: {elixir_end.get('average_rate', 0):,.0f} msg/sec sustained")

        go_endurance = go_end.get('average_rate', 0)
        elixir_endurance = elixir_end.get('average_rate', 0)

        if go_endurance > elixir_endurance:
            print(f"   🥇 GO WINS (better sustained performance)")
        elif elixir_endurance > go_endurance:
            print(f"   🥇 ELIXIR WINS (better sustained performance)")
        else:
            print(f"   🤝 TIE!")

def main():
    go_file, elixir_file = find_latest_results()

    print(f"🔍 Found results:")
    print(f"   Go:     {go_file or 'None'}")
    print(f"   Elixir: {elixir_file or 'None'}")
    print()

    go_results = load_results(go_file)
    elixir_results = load_results(elixir_file)

    if go_results and elixir_results:
        compare_results(go_results, elixir_results)
    else:
        print("❌ Missing results files. Run both benchmarks first!")

if __name__ == "__main__":
    main()
