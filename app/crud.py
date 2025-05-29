from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sa_update, delete as sa_delete
from .models import Task, TaskLog
from .schemas import TaskCreate, TaskUpdate
from sqlalchemy.exc import NoResultFound
from typing import List, Optional
from sqlalchemy.orm import selectinload

async def create_task(db: AsyncSession, task: TaskCreate) -> Task:
    db_task = Task(**task.model_dump(), status="pending")
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    await log_status(db, db_task.id, db_task.status)
    return db_task

async def get_tasks(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    title: Optional[str] = None,
    status: Optional[str] = None,
) -> List[Task]:
    query = select(Task)
    if title:
        query = query.where(Task.title.ilike(f"%{title}%"))
    if status:
        query = query.where(Task.status == status)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_task(db: AsyncSession, task_id: int) -> Optional[Task]:
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.logs))  # Eager load the relationship!
        .where(Task.id == task_id)
    )
    return result.scalar_one_or_none()

async def update_task(db: AsyncSession, task_id: int, task_in: TaskUpdate) -> Optional[Task]:
    db_task = await get_task(db, task_id)
    if not db_task:
        return None
    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(db_task, field, value)
    await db.commit()
    await db.refresh(db_task)
    if task_in.status:
        await log_status(db, db_task.id, db_task.status)
    return db_task

async def delete_task(db: AsyncSession, task_id: int) -> bool:
    db_task = await get_task(db, task_id)
    if not db_task:
        return False
    await db.delete(db_task)
    await db.commit()
    return True

async def log_status(db: AsyncSession, task_id: int, status: str):
    db_log = TaskLog(task_id=task_id, status=status)
    db.add(db_log)
    await db.commit()
