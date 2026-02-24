from fastapi import FastAPI, HTTPException, Request
import sqlite3, logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("app")

app = FastAPI()
DB="app.db"

@app.on_event("startup")
def init():
    con=sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS users(u TEXT,p TEXT)")
    con.execute("INSERT OR IGNORE INTO users(u,p) VALUES('admin','admin')")
    con.commit()
    con.close()

@app.post("/login")
async def login(req: Request):
    b=await req.json()
    u=b.get("username","")
    p=b.get("password","")
    q=f"SELECT 1 FROM users WHERE u='{u}' AND p='{p}'"  # SQL Injection intencional
    con=sqlite3.connect(DB)
    ok=con.execute(q).fetchone()
    con.close()
    if not ok:
        log.warning(f"login_failed user={u} ip={req.client.host}")
        raise HTTPException(401,"bad creds")
    log.info(f"login_ok user={u} ip={req.client.host}")
    return {"ok": True}

@app.get("/boom")
def boom():
    log.error("forced_500")
    1/0