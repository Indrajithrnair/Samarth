from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import json
import os
from data_scraper import DataScraper
from query_processor import QueryProcessor
from logger import samarth_logger
from data_validator import data_validator
import time

app = FastAPI(title="Project Samarth - Government Data Q&A")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize components
data_scraper = DataScraper()
query_processor = QueryProcessor()

class QueryRequest(BaseModel):
    question: str

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.post("/api/query")
async def process_query(request: QueryRequest):
    start_time = time.time()
    try:
        # Process the natural language query with full logging
        result = await query_processor.process_question(request.question)
        
        # Log successful query
        response_time = time.time() - start_time
        samarth_logger.log_query(
            question=request.question,
            entities=result.get("entities", {}),
            data_sources=result.get("sources", []),
            response_time=response_time,
            success=True
        )
        
        return {
            "answer": result["answer"], 
            "sources": result["sources"],
            "quality_report": result.get("quality_report", ""),
            "response_time": f"{response_time:.2f}s"
        }
    except Exception as e:
        # Log failed query
        response_time = time.time() - start_time
        samarth_logger.log_error("query_processing", str(e), {"question": request.question})
        samarth_logger.log_query(
            question=request.question,
            entities={},
            data_sources=[],
            response_time=response_time,
            success=False
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    health_metrics = samarth_logger.get_system_health()
    return {
        "status": "healthy",
        "metrics": health_metrics,
        "data_sources": {
            "agricultural": "connected",
            "climate": "connected", 
            "market_prices": "connected"
        }
    }

@app.get("/api/audit")
async def get_audit_log():
    """Export audit log for compliance and monitoring"""
    return {
        "system_health": samarth_logger.get_system_health(),
        "recent_queries": samarth_logger.query_log[-10:],  # Last 10 queries
        "data_quality": "See individual query responses for detailed quality reports"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)