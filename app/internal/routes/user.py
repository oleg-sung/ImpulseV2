from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1"
)


@router.get('/registor/')
async def user_register():
    return {"message": "Hello"}
