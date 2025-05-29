from fastapi import FastAPI, Depends, HTTPException, Request, status, BackgroundTasks, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.background_tasks import process_task_background
from app import database, models, schemas, crud
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

app = FastAPI(title="Async Task Management API")

# @app.on_event("startup")
# async def on_startup():
#     # Run migrations here in production
#     async with database.engine.begin() as conn:
#         await conn.run_sync(models.Base.metadata.create_all)

# ========== GLOBAL EXCEPTION HANDLING ==========

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Custom 422 response
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    # Handles DB errors
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error occurred."},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Handles all unexpected errors
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error."},
    )

@app.post("/tasks", response_model=schemas.TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(task: schemas.TaskCreate, db: AsyncSession = Depends(database.get_db)):
    try:
        db_task = await crud.create_task(db, task)
        return db_task
    except IntegrityError:
        # Handles unique constraint violations, etc.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task creation failed: duplicate or invalid data.")
    except Exception as e:
        # Log e if needed
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create task: {e}")

@app.get("/tasks", response_model=List[schemas.TaskOut])
async def list_tasks(
    skip: int = 0, 
    limit: int = 10,
    title: Optional[str] = None,
    task_status: Optional[str] = None,
    db: AsyncSession = Depends(database.get_db),
):
    try:
        tasks = await crud.get_tasks(db, skip=skip, limit=limit, title=title, status=task_status)
        return tasks
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch tasks: {e}")

@app.get("/tasks/{task_id}", response_model=schemas.TaskDetail)
async def get_task(task_id: int, db: AsyncSession = Depends(database.get_db)):
    try:
        db_task = await crud.get_task(db, task_id)
        if not db_task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return db_task
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fetch task: {e}")

@app.put("/tasks/{task_id}", response_model=schemas.TaskOut)
async def update_task(
    task_id: int, 
    task_update: schemas.TaskUpdate,
    db: AsyncSession = Depends(database.get_db)
):
    try:
        db_task = await crud.update_task(db, task_id, task_update)
        if not db_task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return db_task
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Update failed due to integrity error: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update task: {e}")

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: AsyncSession = Depends(database.get_db)):
    try:
        deleted = await crud.delete_task(db, task_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete task: {e}")

@app.post("/tasks/{task_id}/process", status_code=status.HTTP_202_ACCEPTED)
async def process_task(
    task_id: int, 
    background_tasks: BackgroundTasks, 
    db: AsyncSession = Depends(database.get_db)
):
    try:
        task = await crud.get_task(db, task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        background_tasks.add_task(process_task_background, db, task_id)
        return {"message": "Task processing started"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to start background processing: {e}")
