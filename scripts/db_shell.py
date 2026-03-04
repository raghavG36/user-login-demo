#!/usr/bin/env python3
"""Open a SQLite shell for app.db. Run from project root: python scripts/db_shell.py"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.db")
if not os.path.exists(db_path):
    print(f"Database not found: {db_path}")
    print("Start the app once so it creates app.db, then run this again.")
    raise SystemExit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # access columns by name

print("Tables:", [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()])
print("Commands: .tables  .schema  .schema users  SELECT * FROM users;  .quit")
print("You can run any SQL: CREATE TABLE ..., INSERT ..., etc.")
print()

# Simple REPL
while True:
    try:
        line = input("sqlite> ").strip()
        if not line:
            continue
        if line in (".quit", ".exit", "exit"):
            break
        if line == ".tables":
            for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"):
                print(r[0])
            continue
        if line.startswith(".schema"):
            table = line.split()[-1] if len(line.split()) > 1 else None
            for r in conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND (name=? OR ? IS NULL)", (table, table)):
                print(r[0] or "")
            continue
        cur = conn.execute(line)
        rows = cur.fetchall()
        if line.strip().upper().startswith("SELECT"):
            if rows:
                for row in rows:
                    print(dict(zip(row.keys(), row)) if hasattr(row, "keys") else row)
            else:
                print("(0 rows)")
        else:
            conn.commit()  # persist CREATE TABLE, INSERT, UPDATE, DELETE
            print("Done.", cur.rowcount if cur.rowcount >= 0 else "")
    except sqlite3.Error as e:
        print("Error:", e)
    except EOFError:
        break

conn.close()
