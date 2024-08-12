#!/usr/bin/env python3
import os, sys, json, time, argparse, urllib.request

def rpc(url, method, params=None):
    data = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params or []}).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        j = json.loads(r.read().decode())
    if "error" in j:
        raise RuntimeError(j["error"])
    return j["result"]

def main():
    p = argparse.ArgumentParser(description="Bridge fee estimator using gas*bytes heuristic")
    p.add_argument("--bytes", type=int, default=1200)
    p.add_argument("--gas-overhead", type=int, default=85000)
    p.add_argument("--markup", type=float, default=1.12)
    p.add_argument("--rpc", default=os.getenv("RPC_URL"))
    args = p.parse_args()
    if not args.rpc:
        print("Set --rpc or RPC_URL"); sys.exit(2)

    gas_price_hex = rpc(args.rpc, "eth_gasPrice")
    gas_price_wei = int(gas_price_hex, 16)
    l1_fee_wei = gas_price_wei * (args.gas_overhead + args.bytes * 16)
    est_fee_wei = int(l1_fee_wei * args.markup)

    out = {
        "timestamp": int(time.time()),
        "rpc": args.rpc,
        "gas_price_wei": gas_price_wei,
        "l1_overhead_gas": args.gas_overhead,
        "calldata_bytes": args.bytes,
        "fee_wei_no_markup": l1_fee_wei,
        "fee_wei_estimate": est_fee_wei
    }
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
