from fastapi import FastAPI
from fastapi.responses import JSONResponse
from server.routers.main import router  # Import the FastAPI router

# Create the FastAPI app
app = FastAPI(
    title="FundSim API",
    description="API Documentation for FundSim",
    version="1.0.0"
)

# Root route for testing


@app.get("/", summary="Root Endpoint", response_description="Welcome message")
def root():
    """
    Root Endpoint
    """
    return JSONResponse(content={"message": "Welcome to the FastAPI-based ASGI app!"})


# Register the FastAPI router
app.include_router(router)

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=1234, reload=True)
