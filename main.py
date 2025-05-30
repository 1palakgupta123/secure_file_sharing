from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, ops, client

app = FastAPI(
    title="Secure File Sharing API",
    description="Backend API for secure file upload, download, and management",
    version="1.0.0",
    docs_url="/docs",        
    redoc_url="/redocs"      
)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route includes
app.include_router(auth.router, prefix="/auth")
app.include_router(ops.router, prefix="/ops")
app.include_router(client.router, prefix="/client")

# Root endpoint
@app.get("/")
def home():
    return {"msg": "Secure File Sharing API is running on port 8080"}

# Run the app on port 8080 permanently
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
