from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import get_connection
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

SECRET_KEY = "SUA_CHAVE_SECRETA_AQUI"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()  


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")


@app.post("/login")
def login(email: str = Form(...), senha: str = Form(...)):
    conn = get_connection()
    if not conn:
        return {"status": "erro", "mensagem": "Erro na conexão com o banco"}

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios_sistema WHERE email=%s", (email,))
    usuario = cursor.fetchone()
    
    cursor.close()
    conn.close()

    if not usuario:
        return {"status": "erro", "mensagem": "Usuário não encontrado"}

    if not pwd_context.verify(senha, usuario["senha_hash"]):
        return {"status": "erro", "mensagem": "Senha incorreta"}

    token = create_access_token({"user_id": usuario["id_usuario"]})

    return {
        "status": "ok",
        "token": token,
        "usuario": {
            "id": usuario["id_usuario"],
            "nome": usuario["nome"],
            "cargo": usuario["cargo"]
        }
    }

@app.post("/logout")
def logout():
    return {"status": "ok", "mensagem": "Logout realizado"}

@app.get("/dashboard")
def dashboard(user_id: int = Depends(verify_token)):
    return {"mensagem": f"Bem-vindo ao dashboard, usuário {user_id}"}
