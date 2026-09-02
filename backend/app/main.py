from fastapi import FastAPI
from app.routes import auth
from app.routes import problem
from app.routes import sessions
from app.routes import chat
from app.routes import analysis
from app.routes import test_cases
app = FastAPI(title="CodeMentor API")


app.include_router(chat.router)

app.include_router(auth.router)
app.include_router(problem.router)


app.include_router(test_cases.router)
app.include_router(analysis.router)
app.include_router(sessions.router)  