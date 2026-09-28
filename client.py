"""Write-Ahead Logging (WAL) & ARIES Crash Recovery Engine
100% Python Standard Library.
"""

class WALRecoveryEngine:
    """ARIES analysis, redo, and undo log recovery engine."""
    def __init__(self):
        self.log = []
        self.db_state = {}
        self.next_lsn = 100

    def append_log(self, trans_id, page_id, old_val, new_val):
        lsn = self.next_lsn
        self.next_lsn += 10
        record = {
            "lsn": lsn,
            "trans_id": trans_id,
            "page_id": page_id,
            "old_val": old_val,
            "new_val": new_val,
            "type": "UPDATE"
        }
        self.log.append(record)
        self.db_state[page_id] = new_val
        return lsn

    def commit(self, trans_id):
        lsn = self.next_lsn
        self.next_lsn += 10
        self.log.append({"lsn": lsn, "trans_id": trans_id, "type": "COMMIT"})
        return lsn

    def recover(self, initial_flushed_state):
        recovered_state = dict(initial_flushed_state)
        active_trans = set()
        for rec in self.log:
            t = rec["trans_id"]
            if rec["type"] == "UPDATE":
                active_trans.add(t)
                recovered_state[rec["page_id"]] = rec["new_val"]
            elif rec["type"] == "COMMIT":
                active_trans.discard(t)

        for rec in reversed(self.log):
            if rec["type"] == "UPDATE" and rec["trans_id"] in active_trans:
                recovered_state[rec["page_id"]] = rec["old_val"]

        return {
            "recovered_state": recovered_state,
            "uncommitted_rolled_back": list(active_trans)
        }
