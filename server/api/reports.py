"""
Reports API Endpoints

This module provides API endpoints for generating and downloading reports
in various formats (TXT, CSV, XLSX, PDF).
"""

import io
import json # For serializing metadata for Redis
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, Response
from fastapi.responses import StreamingResponse
from typing import Dict, List, Any, Union # Removed Optional as it was unused
from pydantic import BaseModel
import uuid
import time
import logging
from datetime import datetime

from ..utils import report_generator
from ..utils.cache import redis_client, REDIS_AVAILABLE, DEFAULT_TTL # Import Redis utils

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

router = APIRouter(prefix="/reports", tags=["reports"])

# REPORTS_CACHE = {} # Removed in-memory cache

REPORT_META_TTL = DEFAULT_TTL + 300 # Metadata lives slightly longer than content
REPORT_CONTENT_TTL = DEFAULT_TTL
REPORT_ERROR_TTL = 300 # 5 minutes for error states

class ReportRequest(BaseModel):
    report_type: str = "trend"  # "trend" or "compare"
    format: str = "pdf"  # "txt", "csv", "xlsx", "pdf"
    data: Dict[str, Any]
    include_charts: bool = True

class ReportStatusData(BaseModel):
    report_id: str
    status: str
    message: str
    format: Union[str, None] = None
    created_at: Union[str, None] = None
    download_url: Union[str, None] = None
    error_detail: Union[str, None] = None

class ReportResponse(BaseModel):
    #This model was previously: status: str, message: str, data: Dict[str,Any]
    #Adjusting to better fit endpoint responses.
    report_id: str
    status: str
    message: str
    download_url: Union[str, None] = None
    details: Union[Dict[str, Any], None] = None # For specific error details or other info

def get_report_meta_key(report_id: str) -> str:
    return f"report:{report_id}:meta"

def get_report_content_key(report_id: str) -> str:
    return f"report:{report_id}:content"

def generate_report_task(
    report_id: str,
    report_type: str,
    format_type: str,
    data: Dict[str, Any],
    include_charts: bool
):
    """Background task to generate a report and store in Redis."""
    meta_key = get_report_meta_key(report_id)
    content_key = get_report_content_key(report_id)
    file_ext = get_file_extension(format_type)
    created_iso = datetime.now().isoformat()

    metadata = {
        "report_id": report_id,
        "status": "processing",
        "format": format_type,
        "type": report_type,
        "include_charts": include_charts,
        "created_at": created_iso,
        "file_extension": file_ext,
        "error_detail": None
    }

    if not REDIS_AVAILABLE:
        logging.error(f"Redis not available. Report generation for {report_id} cannot be reliably stored.")
        # Update metadata to reflect error state if we can't use Redis for actual storage
        metadata["status"] = "error"
        metadata["error_detail"] = "Redis not available, report processing aborted."
        # Try to set this error state in Redis if it becomes available briefly, or log it.
        # For now, this task won't be able to store anything effectively.
        return

    try:
        redis_client.setex(meta_key, REPORT_META_TTL, json.dumps(metadata))
        logging.info(f"Starting report generation for ID: {report_id}, Type: {report_type}, Format: {format_type}")
        
        report_content_obj = report_generator.generate_report(
            data=data,
            format_type=format_type,
            report_type=report_type,
            include_charts=include_charts
        )

        content_to_store: bytes
        if isinstance(report_content_obj, str): # TXT, CSV
            content_to_store = report_content_obj.encode('utf-8')
        elif isinstance(report_content_obj, io.BytesIO): # XLSX, PDF
            content_to_store = report_content_obj.getvalue()
        else:
            raise TypeError(f"Unexpected report content type: {type(report_content_obj)}")

        redis_client.setex(content_key, REPORT_CONTENT_TTL, content_to_store)
        
        metadata["status"] = "completed"
        redis_client.setex(meta_key, REPORT_META_TTL, json.dumps(metadata))
        logging.info(f"Report {report_id} generated and stored successfully.")
        
    except Exception as e:
        logging.error(f"Error generating report ID {report_id}: {e}", exc_info=True)
        metadata["status"] = "error"
        metadata["error_detail"] = str(e)
        if REDIS_AVAILABLE: # Ensure Redis is still available before trying to set error state
            redis_client.setex(meta_key, REPORT_ERROR_TTL, json.dumps(metadata))
        # If content key was created and then error, it might be orphaned. Consider deleting.
        # redis_client.delete(content_key) # Or let it expire

def get_file_extension(format_type: str) -> str:
    """Get file extension for a report format"""
    extensions = {
        "txt": "txt",
        "csv": "csv",
        "xlsx": "xlsx",
        "pdf": "pdf"
    }
    return extensions.get(format_type, "txt")

def get_content_type(format_type: str) -> str:
    """Get content type for a report format"""
    content_types = {
        "txt": "text/plain",
        "csv": "text/csv",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pdf": "application/pdf"
    }
    return content_types.get(format_type, "text/plain")

@router.post("", response_model=ReportResponse)
async def generate_report_endpoint(
    report_request: ReportRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a report in the specified format
    
    - **report_type**: Type of report ("trend" or "compare")
    - **format**: Report format ("txt", "csv", "xlsx", "pdf")
    - **data**: Data to include in the report
    - **include_charts**: Whether to include charts in PDF/Excel reports
    """
    try:
        # Validate report type
        if report_request.report_type not in ["trend", "compare"]:
            raise HTTPException(status_code=400, detail="Invalid report type")
        
        # Validate format
        if report_request.format not in ["txt", "csv", "xlsx", "pdf"]:
            raise HTTPException(status_code=400, detail="Invalid report format")
        
        # Generate a unique ID for the report
        report_id = str(uuid.uuid4())
        meta_key = get_report_meta_key(report_id)

        if not REDIS_AVAILABLE:
            logging.error("Redis not available. Cannot initiate report generation.")
            raise HTTPException(status_code=503, detail="Report generation service temporarily unavailable due to Redis issue.")

        # Initial metadata to indicate task is queued
        initial_metadata = {
            "report_id": report_id,
            "status": "queued",
            "format": report_request.format,
            "type": report_request.report_type,
            "include_charts": report_request.include_charts,
            "created_at": datetime.now().isoformat(),
            "file_extension": get_file_extension(report_request.format),
            "error_detail": None
        }
        redis_client.setex(meta_key, REPORT_META_TTL, json.dumps(initial_metadata))

        # Start report generation in the background
        background_tasks.add_task(
            generate_report_task,
            report_id=report_id,
            report_type=report_request.report_type,
            format_type=report_request.format,
            data=report_request.data,
            include_charts=report_request.include_charts
        )
        
        return {
            "report_id": report_id,
            "status": "queued",
            "message": f"Report generation initiated. Check status at /reports/status/{report_id}",
            "download_url": f"/reports/download/{report_id}" # This URL is for when it's ready
            # "details": initial_metadata # Optionally return initial metadata
        }
        
    except HTTPException: # Re-raise if it's already an HTTPException
        raise
    except Exception as e:
        logging.error(f"Error initiating report generation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to initiate report generation: {str(e)}")

@router.get("/status/{report_id}", response_model=ReportStatusData)
async def get_report_status_endpoint(
    report_id: str
):
    """
    Check the status of a report generation task
    
    - **report_id**: ID of the report to check
    """
    if not REDIS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Report status service temporarily unavailable due to Redis issue.")

    meta_key = get_report_meta_key(report_id)
    raw_metadata = redis_client.get(meta_key)

    if not raw_metadata:
        # To differentiate between never existed vs. expired, this is okay.
        # If it was processed and expired, it's effectively not found for user.
        return ReportStatusData(
            report_id=report_id,
            status="not_found",
            message="Report not found. It may have expired or the ID is invalid."
        )
    
    metadata = json.loads(raw_metadata.decode('utf-8'))
    status = metadata.get("status", "unknown")
    message = f"Report status: {status}."
    download_url = None

    if status == "completed":
        message = "Report generation completed successfully."
        download_url = f"/reports/download/{report_id}"
    elif status == "error":
        message = f"Report generation failed: {metadata.get('error_detail', 'Unknown error')}"
    elif status == "processing":
        message = "Report generation is currently in progress."
    elif status == "queued":
        message = "Report generation is queued and will start shortly."

    return ReportStatusData(
        report_id=report_id,
        status=status,
        message=message,
        format=metadata.get("format"),
        created_at=metadata.get("created_at"),
        download_url=download_url,
        error_detail=metadata.get("error_detail")
    )

@router.get("/download/{report_id}")
async def download_report_endpoint(
    report_id: str
):
    """
    Download a generated report
    
    - **report_id**: ID of the report to download
    """
    if not REDIS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Report download service temporarily unavailable due to Redis issue.")

    meta_key = get_report_meta_key(report_id)
    content_key = get_report_content_key(report_id)

    raw_metadata = redis_client.get(meta_key)
    if not raw_metadata:
        raise HTTPException(status_code=404, detail="Report metadata not found. Report may have expired or ID is invalid.")
    
    metadata = json.loads(raw_metadata.decode('utf-8'))
    report_status = metadata.get("status")

    if report_status == "error":
        error_detail = metadata.get('error_detail', 'Unknown error during generation.')
        raise HTTPException(status_code=500, detail=f"Report generation failed: {error_detail}")
    
    if report_status != "completed":
        raise HTTPException(status_code=400, detail=f"Report is not yet ready for download. Current status: {report_status}")
    
    report_content_bytes = redis_client.get(content_key)
    if not report_content_bytes:
        # This case implies metadata says completed, but content is missing/expired.
        logging.error(f"Report content for {report_id} not found in Redis, though metadata indicates completion.")
        raise HTTPException(status_code=404, detail="Report content not found. It may have expired prematurely.")

    format_type = metadata["format"]
    file_extension = metadata["file_extension"]
    content_type_header = get_content_type(format_type)
    report_gen_type = metadata["type"]
        
    filename = f"youtrend_report_{report_gen_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"
    
    if format_type in ["txt", "csv"]:
        return Response(
            content=report_content_bytes.decode('utf-8'),
            media_type=content_type_header,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    else: # XLSX, PDF
        return StreamingResponse(
            io.BytesIO(report_content_bytes),
            media_type=content_type_header,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
