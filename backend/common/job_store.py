"""
Job tracking module for asynchronous processing.
This module provides a repository for tracking long-running job status.
"""

import logging
import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from common.datastore import get_data_store

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Enum for job status values"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobStore:
    """
    Repository class for managing job tracking.
    This class provides methods to create, update, and query job status.
    """

    def __init__(self):
        """Initialize the job store with a data store connection"""
        self.data_store = get_data_store()
        self.collection = self.data_store._get_connection().jobs

        # Ensure we have the jobs collection with appropriate indexes
        if "jobs" not in self.data_store._get_connection().list_collection_names():
            self.data_store._get_connection().create_collection("jobs")
            self.collection.create_index([("created_at", -1)])
            self.collection.create_index([("job_id", 1)], unique=True)

        logger.info("JobStore initialized")

    def create_job(self, file_path: str) -> str:
        """
        Create a new job entry

        Args:
            file_path: Path to the uploaded file to process

        Returns:
            job_id: Unique identifier for the job
        """
        job_id = str(uuid.uuid4())
        now = datetime.now(UTC)

        job_data = {
            "job_id": job_id,
            "status": JobStatus.PENDING.value,
            "file_path": file_path,
            "created_at": now,
            "updated_at": now,
            "result": None,
            "error": None,
        }

        self.collection.insert_one(job_data)
        logger.info(f"Created new job with ID: {job_id}")
        return job_id

    def update_job_status(
        self, job_id: str, status: JobStatus, result: Optional[Dict] = None, error: Optional[str] = None
    ) -> bool:
        """
        Update the status of an existing job

        Args:
            job_id: The job identifier
            status: New status value
            result: Optional result data (for completed jobs)
            error: Optional error message (for failed jobs)

        Returns:
            True if successful, False otherwise
        """
        try:
            update_data = {"status": status.value, "updated_at": datetime.now(UTC)}

            if result is not None:
                update_data["result"] = result

            if error is not None:
                update_data["error"] = error

            result = self.collection.update_one({"job_id": job_id}, {"$set": update_data})

            if result.modified_count > 0:
                logger.info(f"Updated job {job_id} status to {status.value}")
                return True
            else:
                logger.warning(f"Failed to update job {job_id}: job not found")
                return False

        except Exception as e:
            logger.error(f"Error updating job {job_id}: {str(e)}")
            return False

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job details by ID

        Args:
            job_id: The job identifier

        Returns:
            Job data dictionary or None if not found
        """
        try:
            job = self.collection.find_one({"job_id": job_id})
            if job:
                # Convert MongoDB ObjectId to string for JSON serialization
                job["_id"] = str(job["_id"])
                # Convert datetime objects to ISO strings
                job["created_at"] = job["created_at"].isoformat()
                job["updated_at"] = job["updated_at"].isoformat()
                return job
            return None
        except Exception as e:
            logger.error(f"Error retrieving job {job_id}: {str(e)}")
            return None

    def get_recent_jobs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent jobs ordered by creation time

        Args:
            limit: Maximum number of jobs to return

        Returns:
            List of job data dictionaries
        """
        try:
            jobs = list(self.collection.find().sort("created_at", -1).limit(limit))

            # Convert MongoDB ObjectId to string and datetime to ISO string for JSON serialization
            for job in jobs:
                job["_id"] = str(job["_id"])
                job["created_at"] = job["created_at"].isoformat()
                job["updated_at"] = job["updated_at"].isoformat()

            return jobs
        except Exception as e:
            logger.error(f"Error retrieving recent jobs: {str(e)}")
            return []
