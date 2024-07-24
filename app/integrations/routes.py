from fastapi import APIRouter

__all__ = ['router']

router = APIRouter(
    prefix="/integrations",
)


@router.post('/push_deal')
@router.get('/push_deal')
async def push_deal():
    return {"success": True}