import sys
import json
from client import WALRecoveryEngine

wal = WALRecoveryEngine()

def handle_rpc(line):
    global wal
    try:
        req = json.loads(line)
    except Exception:
        return
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        res = {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "genpark-wal-write-ahead-log-recovery-skill", "version": "1.0.0"},
            "capabilities": {"tools": {}}
        }
    elif method == "tools/list":
        res = {
            "tools": [
                {
                    "name": "log_update",
                    "description": "Append an UPDATE record to the Write-Ahead Log",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "trans_id": {"type": "string"},
                            "page_id": {"type": "string"},
                            "old_val": {"type": "number"},
                            "new_val": {"type": "number"}
                        },
                        "required": ["trans_id", "page_id", "old_val", "new_val"]
                    }
                },
                {
                    "name": "run_recovery",
                    "description": "Execute ARIES redo and undo passes against initial checkpoint state",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "checkpoint_state": {"type": "object"}
                        },
                        "required": ["checkpoint_state"]
                    }
                }
            ]
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "log_update":
            lsn = wal.append_log(args.get("trans_id"), args.get("page_id"), args.get("old_val"), args.get("new_val"))
            res = {"content": [{"type": "text", "text": json.dumps({"lsn": lsn, "status": "logged"})}]}
        elif tool_name == "run_recovery":
            recovery = wal.recover(args.get("checkpoint_state", {}))
            res = {"content": [{"type": "text", "text": json.dumps(recovery)}]}
        else:
            res = {"isError": True, "content": [{"type": "text", "text": f"Unknown tool {tool_name}"}]}
    else:
        res = {"error": {"code": -32601, "message": "Method not found"}}

    resp = {"jsonrpc": "2.0", "id": req_id, "result": res.get("result", res)}
    sys.stdout.write(json.dumps(resp) + "\n")
    sys.stdout.flush()

def main():
    for line in sys.stdin:
        if line.strip():
            handle_rpc(line.strip())

if __name__ == "__main__":
    main()
