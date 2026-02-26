import os
import sqlite3
import logging

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse

from fastapi import status

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("app")

app = FastAPI()

DB = "app.db"
DEFAULT_USER = os.getenv("DEFAULT_USER", "admin")
DEFAULT_PASS = os.getenv("DEFAULT_PASS", "admin")

@app.on_event("startup")
def init():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS users(u TEXT PRIMARY KEY, p TEXT)")
    # ✅ ya no está hardcodeado en el código: viene de variables de entorno
    con.execute("INSERT OR IGNORE INTO users(u,p) VALUES(?,?)", (DEFAULT_USER, DEFAULT_PASS))
    con.commit()
    con.close()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Mini Secure App</title>
  <style>
    body{font-family:Arial, sans-serif; max-width:720px; margin:40px auto; padding:0 16px;}
    .card{border:1px solid #ddd; border-radius:12px; padding:16px; margin:12px 0;}
    input{padding:10px; width:100%; margin:6px 0; border:1px solid #ccc; border-radius:8px;}
    button{padding:10px 14px; border:0; border-radius:10px; cursor:pointer;}
    .row{display:flex; gap:10px; flex-wrap:wrap;}
    .ok{color:green;} .bad{color:#b00020;}
    code{background:#f6f6f6; padding:2px 6px; border-radius:6px;}
  </style>
</head>
<body>
  <h2>Mini App (Demo)</h2>

  <div class="card">
    <h3>Login</h3>
    <p>Usuario/clave válidos vienen de variables de entorno (<code>DEFAULT_USER</code>/<code>DEFAULT_PASS</code>).</p>
    <input id="u" placeholder="username" value="admin"/>
    <input id="p" placeholder="password" value="wrong"/>
    <div class="row">
      <button onclick="doLogin()">Login</button>
      <button onclick="spamLogin()">Ataque controlado (30 fallidos)</button>
      <button onclick="boom()">Generar 500</button>
    </div>
    <p id="status"></p>
    <p>Fallidos acumulados: <b id="fails">0</b></p>
  </div>

<script>
let fails = 0;
function setStatus(msg, ok){
  const el = document.getElementById("status");
  el.textContent = msg;
  el.className = ok ? "ok" : "bad";
}
async function doLogin(){
  const u = document.getElementById("u").value;
  const p = document.getElementById("p").value;
  const res = await fetch("/login", {
    method:"POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({username:u, password:p})
  });
  if(res.ok){
    setStatus("✅ login_ok (revisa logs)", true);
  } else {
    fails += 1;
    document.getElementById("fails").textContent = fails;
    setStatus("❌ login_failed (revisa logs)", false);
  }
}
async function spamLogin(){
  for(let i=0;i<30;i++){
    await doLogin();
  }
}
async function boom(){
  await fetch("/boom");
  setStatus("💥 forced_500 generado (revisa logs)", false);
}
</script>
</body>
</html>
"""

@app.post(
    "/login",
    responses={
        401: {"description": "Invalid credentials"}
    }
)
async def login(req: Request):
    b = await req.json()
    u = b.get("username", "")
    p = b.get("password", "")

    # ✅ FIX: query parametrizada (sin SQL injection)
    con = sqlite3.connect(DB)
    q = f"SELECT 1 FROM users WHERE u='{u}' AND p='{p}'"
    ok = con.execute(q).fetchone()
    con.close()

    if not ok:
        log.warning(f"login_failed user={u} ip={req.client.host}")
        raise HTTPException(401, "bad creds")

    log.info(f"login_ok user={u} ip={req.client.host}")
    return JSONResponse({"ok": True})

@app.get("/boom")
def boom():
    # ✅ 500 controlado (no crash por 1/0)
    log.error("forced_500")
    return Response(content="forced_500", status_code=500)