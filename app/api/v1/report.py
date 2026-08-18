from datetime import date

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.services.report_service import ReportService
from app.services.pdf_report_service import PDFReportService


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get("/overall")
async def get_overall_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    organization_id: int | None = Query(None),
    team_id: int | None = Query(None),
    calling_agent_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ReportService.get_overall_report_data(
        db=db,
        start_date=start_date,
        end_date=end_date,
        current_user=current_user,
        organization_id=organization_id,
        team_id=team_id,
        calling_agent_id=calling_agent_id,
    )


@router.get("/overall/pdf")
async def get_overall_report_pdf(
    start_date: date = Query(...),
    end_date: date = Query(...),
    organization_id: int | None = Query(None),
    team_id: int | None = Query(None),
    calling_agent_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report_data = await ReportService.get_overall_report_data(
        db=db,
        start_date=start_date,
        end_date=end_date,
        current_user=current_user,
        organization_id=organization_id,
        team_id=team_id,
        calling_agent_id=calling_agent_id,
    )

    pdf_file = PDFReportService.generate_pdf(report_data)

    return Response(
        content=pdf_file.getvalue(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                "attachment; "
                'filename="voiceinsights_report.pdf"'
            )
        },
    )