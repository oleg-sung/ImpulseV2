from celery.result import AsyncResult
from fastapi import APIRouter
from starlette import status

from internal.task.schema import TaskResult
from pkg.celery_tools.tools import celery_app

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/{task_id}/", response_model=TaskResult, status_code=status.HTTP_200_OK)
async def get_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    return TaskResult(
        task_id=task_id, status=task_result.status, result=task_result.result
    )
