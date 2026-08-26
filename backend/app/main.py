from fastapi import FastAPI
from app.routes import auth
from app.routes import problem
app = FastAPI(title="CodeMentor API")


app.include_router(auth.router)
app.include_router(problem.router)
