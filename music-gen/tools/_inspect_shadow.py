import os, json
p = "/home/user/music-gen-instance/fork-87da4f517029/clone-0/promise_ledger.jsonl"
if not os.path.exists(p):
    print("not-found")
    d = os.path.dirname(p)
    if os.path.isdir(d):
        print("dir:", os.listdir(d))
else:
    with open(p) as f:
        lines = f.readlines()
    print(f"lines={len(lines)}")
    for line in lines:
        try:
            e = json.loads(line)
            print(f"  {e.get('milestone_id')} status={e.get('status')}")
        except Exception as ex:
            print(f"  err: {ex}")
