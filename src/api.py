#!/usr/bin/env python3
"""
FastAPI application for the Chess Opening Recommendation System.
Provides REST API with automatic OpenAPI documentation for job-based processing.
"""

import asyncio
import json
import logging
import os
import tempfile
import uuid
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile, BackgroundTasks
from pydantic import BaseModel, Field
import yaml

# Import our components
from src.analyzer import analyze_games

# Load configuration
with open('config.yaml', 'r', encoding='utf-8') as f:
    config: Dict[str, Any] = yaml.safe_load(f)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Chess Opening Recommendation API",
    description="API for analyzing chess games and generating personalized opening recommendations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# File-based job storage (shared across processes)
jobs_dir = Path("data/jobs")
jobs_dir.mkdir(parents=True, exist_ok=True)

# Process pool executor for CPU-intensive tasks
max_workers = config.get('api', {}).get('max_workers', 4)  # Get from config or default to 4
process_pool = ProcessPoolExecutor(max_workers=max_workers)

# Pydantic models for API documentation
class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobResponse(BaseModel):
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    message: str = Field(..., description="Status message")
    created_at: datetime = Field(..., description="Job creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class JobResult(BaseModel):
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    results: Optional[Dict[str, Any]] = Field(None, description="Analysis results")
    error: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Job creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health status")
    service: str = Field(..., description="Service name")
    timestamp: datetime = Field(..., description="Health check timestamp")

def get_job_file_path(job_id: str) -> Path:
    """Get the file path for a job."""
    return jobs_dir / f"{job_id}.json"

def save_job(job_id: str, job_data: Dict[str, Any]) -> None:
    """Save job data to file."""
    job_file = get_job_file_path(job_id)
    # Convert datetime objects to ISO format for JSON serialization
    serializable_data = {}
    for key, value in job_data.items():
        if isinstance(value, datetime):
            serializable_data[key] = value.isoformat()
        else:
            serializable_data[key] = value
    
    with open(job_file, 'w') as f:
        json.dump(serializable_data, f, indent=2)

def load_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Load job data from file."""
    job_file = get_job_file_path(job_id)
    if not job_file.exists():
        return None
    
    with open(job_file, 'r') as f:
        data = json.load(f)
    
    # Convert ISO format strings back to datetime objects
    for key in ['created_at', 'updated_at', 'completed_at']:
        if key in data and data[key]:
            data[key] = datetime.fromisoformat(data[key])
    
    return data

def update_job_status(job_id: str, status: JobStatus, message: str, **kwargs) -> None:
    """Update job status and save to file."""
    job_data = load_job(job_id)
    if job_data is None:
        logger.error(f"Job {job_id} not found for status update")
        return
    
    job_data.update({
        'status': status,
        'message': message,
        'updated_at': datetime.now(),
        **kwargs
    })
    
    save_job(job_id, job_data)

def list_all_jobs() -> List[Dict[str, Any]]:
    """List all jobs from the jobs directory."""
    jobs_list = []
    for job_file in jobs_dir.glob("*.json"):
        job_id = job_file.stem
        job_data = load_job(job_id)
        if job_data:
            jobs_list.append(job_data)
    return jobs_list

def delete_job_file(job_id: str) -> bool:
    """Delete job file from storage."""
    job_file = get_job_file_path(job_id)
    if job_file.exists():
        job_file.unlink()
        return True
    return False

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources when the application shuts down."""
    logger.info("Shutting down application...")
    process_pool.shutdown(wait=True)
    logger.info("Process pool executor shut down")

def run_analysis_in_process(job_id: str, pgn_file_path: str, config_path: str) -> Dict[str, Any]:
    """
    Standalone function to run analysis in a separate process.
    This function can be called from ProcessPoolExecutor.
    
    Args:
        job_id: Job identifier
        pgn_file_path: Path to PGN file
        config_path: Path to config file
        
    Returns:
        Dictionary with results or error information
    """
    try:
        # Load config in the worker process
        with open(config_path, 'r', encoding='utf-8') as f:
            worker_config = yaml.safe_load(f)
        
        # Run the analysis using the analyzer module
        results = analyze_games(pgn_file_path, worker_config)
        
        # Return results with job metadata
        return {
            'job_id': job_id,
            'success': True,
            'results': results
        }
        
    except Exception as e:
        return {
            'job_id': job_id,
            'success': False,
            'error': str(e)
        }

async def process_job(job_id: str, pgn_file_path: str):
    """
    Background task to process a chess analysis job.
    
    Args:
        job_id: Unique job identifier
        pgn_file_path: Path to the PGN file to analyze
    """
    start_time = datetime.now()
    
    try:
        # Update job status to processing
        update_job_status(job_id, JobStatus.PROCESSING, "Processing PGN file...")
        
        # Run analysis in a separate process to avoid blocking the event loop
        # Add timeout protection (default 30 minutes)
        timeout_seconds = config.get('api', {}).get('job_timeout', 1800)  # 30 minutes default
        
        loop = asyncio.get_event_loop()
        process_result = await asyncio.wait_for(
            loop.run_in_executor(
                process_pool, 
                run_analysis_in_process, 
                job_id, 
                pgn_file_path,
                'config.yaml'  # Pass config file path
            ),
            timeout=timeout_seconds
        )
        
        # Update job with results
        completed_at = datetime.now()
        processing_time = (completed_at - start_time).total_seconds()
        
        if process_result['success']:
            update_job_status(
                job_id, 
                JobStatus.COMPLETED, 
                "Analysis completed successfully", 
                results=process_result['results'], 
                completed_at=completed_at, 
                processing_time=processing_time
            )
            logger.info(f"Job {job_id} completed successfully in {processing_time:.2f} seconds")
        else:
            update_job_status(
                job_id, 
                JobStatus.FAILED, 
                f"Analysis failed: {process_result['error']}", 
                error=process_result['error']
            )
            logger.error(f"Job {job_id} failed: {process_result['error']}")
        
    except asyncio.TimeoutError:
        error_msg = f"Analysis timed out after {timeout_seconds} seconds"
        logger.error(f"Job {job_id} timed out: {error_msg}")
        update_job_status(job_id, JobStatus.FAILED, error_msg, error=error_msg)
        
    except Exception as e:
        error_msg = f"Analysis failed: {str(e)}"
        logger.error(f"Job {job_id} failed: {error_msg}")
        update_job_status(job_id, JobStatus.FAILED, error_msg, error=error_msg)

@app.post("/jobs", response_model=JobResponse, summary="Submit Analysis Job")
async def submit_job(
    background_tasks: BackgroundTasks,
    pgn_file: UploadFile = File(..., description="PGN file to analyze")
):
    """
    Submit a new chess analysis job.
    
    Upload a PGN file to start the analysis process. The job will be processed
    asynchronously and you can check the status using the returned job_id.
    
    - **pgn_file**: PGN file containing chess games to analyze
    
    Returns a job_id that can be used to check status and retrieve results.
    """
    # Validate file
    if not pgn_file.filename.lower().endswith('.pgn'):
        raise HTTPException(status_code=400, detail="Please upload a PGN file")
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    created_at = datetime.now()
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pgn') as tmp_file:
            content = await pgn_file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Create job record
        save_job(job_id, {
            'job_id': job_id,
            'status': JobStatus.PENDING,
            'message': "Job submitted successfully",
            'created_at': created_at,
            'updated_at': created_at,
            'pgn_file_path': tmp_file_path
        })
        
        # Start background processing
        background_tasks.add_task(process_job, job_id, tmp_file_path)
        
        return JobResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
            message="Job submitted successfully",
            created_at=created_at,
            updated_at=created_at
        )
        
    except Exception as e:
        logger.error(f"Error submitting job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error submitting job: {str(e)}")

@app.get("/jobs/{job_id}", response_model=JobResult, summary="Get Job Status")
async def get_job_status(job_id: str):
    """
    Get the status and results of a chess analysis job.
    
    - **job_id**: The job identifier returned from the submit endpoint
    
    Returns the current status and results if completed.
    """
    job_data = load_job(job_id)
    if job_data is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobResult(
        job_id=job_data['job_id'],
        status=job_data['status'],
        results=job_data.get('results'),
        error=job_data.get('error'),
        created_at=job_data['created_at'],
        completed_at=job_data.get('completed_at'),
        processing_time=job_data.get('processing_time')
    )

@app.get("/jobs", response_model=List[JobResponse], summary="List All Jobs")
async def list_jobs():
    """
    List all submitted jobs with their current status.
    
    Returns a list of all jobs with their status and metadata.
    """
    job_list = []
    for job_data in list_all_jobs():
        job_list.append(JobResponse(
            job_id=job_data['job_id'],
            status=job_data['status'],
            message=job_data['message'],
            created_at=job_data['created_at'],
            updated_at=job_data['updated_at']
        ))
    
    return job_list

@app.delete("/jobs/{job_id}", summary="Delete Job")
async def delete_job(job_id: str):
    """
    Delete a job and clean up associated resources.
    
    - **job_id**: The job identifier to delete
    
    Removes the job from the system and cleans up temporary files.
    """
    job_data = load_job(job_id)
    if job_data is None:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Clean up temporary file if it exists
    pgn_file_path = job_data.get('pgn_file_path')
    if pgn_file_path and os.path.exists(pgn_file_path):
        try:
            os.unlink(pgn_file_path)
        except Exception as e:
            logger.warning(f"Could not delete temporary file {pgn_file_path}: {e}")
    
    # Remove job from storage
    if delete_job_file(job_id):
        return {"message": f"Job {job_id} deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete job")

@app.get("/health", response_model=HealthResponse, summary="Health Check")
async def health_check():
    """
    Check the health status of the API service.
    
    Returns the current health status and service information.
    """
    return HealthResponse(
        status="healthy",
        service="chess-recommender-api",
        timestamp=datetime.now()
    )

@app.get("/", summary="API Information")
async def root():
    """
    Get API information and available endpoints.
    
    Returns basic information about the API and links to documentation.
    """
    return {
        "service": "Chess Opening Recommendation API",
        "version": "1.0.0",
        "description": "API for analyzing chess games and generating personalized opening recommendations",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_spec": "/openapi.json"
        },
        "endpoints": {
            "submit_job": "POST /jobs",
            "get_job_status": "GET /jobs/{job_id}",
            "list_jobs": "GET /jobs",
            "delete_job": "DELETE /jobs/{job_id}",
            "health_check": "GET /health"
        }
    }

if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host='0.0.0.0', port=port) 