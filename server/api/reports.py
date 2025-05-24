"""
Reports API Endpoints

This module provides API endpoints for generating and downloading reports
in various formats (TXT, CSV, XLSX, PDF).
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, Response
from fastapi.responses import StreamingResponse
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel
import json
import os
import uuid
import time
from datetime import datetime

from utils import youtube_api, data_processor, report_generator

router = APIRouter(prefix="/api/reports", tags=["reports"])

# Store generated reports in memory (in a production environment, use Redis or another storage)
REPORTS_CACHE = {}

# Request and response models
class ReportRequest(BaseModel):
    report_type: str = "trend"  # "trend" or "compare"
    format: str = "pdf"  # "txt", "csv", "xlsx", "pdf"
    data: Dict[str, Any]
    include_charts: bool = True

class ReportResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any]

def generate_report_task(
    report_id: str,
    report_type: str,
    format_type: str,
    data: Dict[str, Any],
    include_charts: bool
):
    """Background task to generate a report"""
    try:
        # Generate the report
        report_content = report_generator.generate_report(
            data=data,
            format_type=format_type,
            report_type=report_type,
            include_charts=include_charts
        )
        
        # Store the report in cache with metadata
        REPORTS_CACHE[report_id] = {
            "content": report_content,
            "format": format_type,
            "type": report_type,
            "created_at": datetime.now().isoformat(),
            "expires_at": time.time() + 3600,  # Expire after 1 hour
            "file_extension": get_file_extension(format_type)
        }
        
    except Exception as e:
        # Store error in cache
        REPORTS_CACHE[report_id] = {
            "error": str(e),
            "created_at": datetime.now().isoformat(),
            "expires_at": time.time() + 300  # Expire after 5 minutes
        }

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
async def generate_report(
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
            "status": "success",
            "message": f"Report generation started. Use the download endpoint to retrieve it.",
            "data": {
                "report_id": report_id,
                "format": report_request.format,
                "download_url": f"/api/reports/download/{report_id}"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{report_id}", response_model=ReportResponse)
async def get_report_status(
    report_id: str
):
    """
    Check the status of a report generation task
    
    - **report_id**: ID of the report to check
    """
    try:
        if report_id not in REPORTS_CACHE:
            return {
                "status": "pending",
                "message": "Report generation in progress or not found",
                "data": {
                    "report_id": report_id
                }
            }
        
        report_info = REPORTS_CACHE[report_id]
        
        if "error" in report_info:
            return {
                "status": "error",
                "message": f"Report generation failed: {report_info['error']}",
                "data": {
                    "report_id": report_id,
                    "created_at": report_info["created_at"]
                }
            }
        
        if "content" in report_info:
            return {
                "status": "completed",
                "message": "Report generation completed",
                "data": {
                    "report_id": report_id,
                    "format": report_info["format"],
                    "created_at": report_info["created_at"],
                    "download_url": f"/api/reports/download/{report_id}"
                }
            }
        
        return {
            "status": "pending",
            "message": "Report generation in progress",
            "data": {
                "report_id": report_id
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{report_id}")
async def download_report(
    report_id: str
):
    """
    Download a generated report
    
    - **report_id**: ID of the report to download
    """
    try:
        if report_id not in REPORTS_CACHE:
            raise HTTPException(status_code=404, detail="Report not found")
        
        report_info = REPORTS_CACHE[report_id]
        
        if "error" in report_info:
            raise HTTPException(status_code=500, detail=f"Report generation failed: {report_info['error']}")
        
        if "content" not in report_info:
            raise HTTPException(status_code=400, detail="Report generation in progress")
        
        format_type = report_info["format"]
        content = report_info["content"]
        file_extension = report_info["file_extension"]
        content_type = get_content_type(format_type)
        
        # Create filename
        filename = f"youtrend_report_{report_info['type']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"
        
        # Handle different report formats
        if format_type in ["txt", "csv"]:
            # Text-based formats
            return Response(
                content=content,
                media_type=content_type,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:
            # Binary formats (XLSX, PDF)
            return StreamingResponse(
                iter([content.getvalue()]),
                media_type=content_type,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
