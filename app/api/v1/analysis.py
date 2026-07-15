from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.analysis import AnalysisResponse
from app.services.analysis_service import AnalysisService

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)


@router.post(
    "/generate/{transcript_id}",
    response_model=AnalysisResponse
)
async def generate_analysis(
    transcript_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        return await AnalysisService.analyze_transcript(
            db,
            transcript_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=list[AnalysisResponse]
)
async def get_all_analysis(
    db: AsyncSession = Depends(get_db)
):
    return await AnalysisService.get_all_analysis(db)


@router.get(
    "/{analysis_id}",
    response_model=AnalysisResponse
)
async def get_analysis(
    analysis_id: int,
    db: AsyncSession = Depends(get_db)
):
    analysis = await AnalysisService.get_analysis(
        db,
        analysis_id
    )

    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found."
        )

    return analysis