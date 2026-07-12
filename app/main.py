from fastapi import FastAPI

app = FastAPI(
    title="AI Document Intelligence Platform",
    description="Backend application for intelligent document management, AI-powered search, workflow automation, and cloud-native deployment.",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Document Intelligence Platform"
    }