import asyncio

from app.schemas import TaskUpdate
from .crud import update_task, log_status, get_task
from sqlalchemy.ext.asyncio import AsyncSession

async def process_task_background(db: AsyncSession, task_id: int):
    task = await get_task(db, task_id)
    if not task:
        return
    # Set status to in_progress
    await update_task(db, task_id, TaskUpdate(status="in_progress"))
    await log_status(db, task_id, "in_progress")

    # Simulate a long-running job
    await asyncio.sleep(5)

    # Set status to completed
    await update_task(db, task_id, TaskUpdate(status="completed"))
    await log_status(db, task_id, "completed")
