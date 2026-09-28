from client import WALRecoveryEngine

def main():
    wal = WALRecoveryEngine()
    wal.append_log("T1", "page_10", 100, 200)
    wal.commit("T1")
    wal.append_log("T2", "page_10", 200, 300) # uncommitted crash
    res = wal.recover({"page_10": 100})
    print("WAL & ARIES Recovery Verification:")
    print(f"Recovered State: {res['recovered_state']}")
    print(f"Rolled Back Transactions: {res['uncommitted_rolled_back']}")

if __name__ == "__main__":
    main()
