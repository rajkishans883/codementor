from fastapi import FastAPI

app = FastAPI(title="CodeMentor API")

@app.get("/")
def root():
    return {"message": "CodeMentor API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}