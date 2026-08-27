from collections import Counter, defaultdict
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.report_repository import ReportRepository
from app.models.user import User


class ReportService:

    @staticmethod
    def has_violation(value):
        if value is None:
            return False

        normalized = str(value).strip().lower()

        return normalized not in {
            "",
            "none",
            "no violation",
            "no violations",
            "null",
        }

    @staticmethod
    async def get_overall_report_data(
        db: AsyncSession,
        current_user: User,
        start_date: date,
        end_date: date,
        calling_agent_id: int | None = None,
        team_id: int | None = None,
        organization_id: int | None = None,
    ):
        rows = await ReportRepository.get_analysis_data(
            db=db,
            current_user=current_user,
            start_date=start_date,
            end_date=end_date,
            calling_agent_id=calling_agent_id,
            team_id=team_id,
            organization_id=organization_id,
        )

        total_calls = len(rows)

        # ---------------------------------------------------------
        # EMPTY REPORT
        # ---------------------------------------------------------

        if total_calls == 0:
            return {
                "organization": {
                    "id": current_user.organization_id,
                    "name": None,
                },
                "team": {
                    "id": current_user.team_id,
                    "name": None,
                },
                "report_period": {
                    "start_date": start_date,
                    "end_date": end_date,
                },
                "summary": {
                    "total_calls": 0,
                    "analyzed_calls": 0,
                    "average_overall_score": 0,
                    "average_compliance": 0,
                    "average_professionalism": 0,
                    "average_empathy": 0,
                },
                "sentiment": {
                    "positive": 0,
                    "neutral": 0,
                    "negative": 0,
                    "other": 0,
                },
                "rules": {
                    "greeting_followed": 0,
                    "greeting_not_followed": 0,
                    "closing_followed": 0,
                    "closing_not_followed": 0,
                },
                "violations": [],
                "daily_performance": [],
                "agent_performance": [],
            }

        # ---------------------------------------------------------
        # HELPERS
        # ---------------------------------------------------------

        def average(values):
            values = [
                value
                for value in values
                if value is not None
            ]

            if not values:
                return 0

            return round(
                sum(values) / len(values),
                2,
            )

        # ---------------------------------------------------------
        # ORGANIZATION / TEAM
        # ---------------------------------------------------------

        organization = None
        team = None

        # Repository now returns:
        #
        # Analysis
        # Media
        # Agent
        # Organization
        # Team

        for _, _, agent, org, current_team in rows:
            if org:
                organization = org

            if current_team:
                team = current_team

            if organization and team:
                break

        # ---------------------------------------------------------
        # SCORE COLLECTIONS
        # ---------------------------------------------------------

        overall_scores = []
        compliance_scores = []
        professionalism_scores = []
        empathy_scores = []

        # ---------------------------------------------------------
        # SENTIMENT
        # ---------------------------------------------------------

        positive = 0
        neutral = 0
        negative = 0
        other = 0

        # ---------------------------------------------------------
        # RULES
        # ---------------------------------------------------------

        greeting_followed = 0
        greeting_not_followed = 0

        closing_followed = 0
        closing_not_followed = 0

        # ---------------------------------------------------------
        # DAILY PERFORMANCE
        # ---------------------------------------------------------

        daily_data = defaultdict(
            lambda: {
                "calls": 0,
                "overall_scores": [],
                "compliance_scores": [],
                "professionalism_scores": [],
                "empathy_scores": [],
                "violations": 0,
            }
        )

        # ---------------------------------------------------------
        # AGENT PERFORMANCE
        # ---------------------------------------------------------

        agent_data = defaultdict(
            lambda: {
                "agent_id": None,
                "agent_name": "Unassigned",
                "team_id": None,
                "team_name": None,
                "organization_id": None,
                "organization_name": None,
                "calls": 0,
                "overall_scores": [],
                "compliance_scores": [],
                "professionalism_scores": [],
                "empathy_scores": [],
                "violations": 0,
            }
        )

        violation_counter = Counter()

        # ---------------------------------------------------------
        # PROCESS CALLS
        # ---------------------------------------------------------

        for analysis, media, agent, org, current_team in rows:

            # -----------------------------------------------------
            # Overall scores
            # -----------------------------------------------------

            if analysis.overall_score is not None:
                overall_scores.append(
                    analysis.overall_score
                )

            if analysis.compliance_score is not None:
                compliance_scores.append(
                    analysis.compliance_score
                )

            if analysis.professionalism_score is not None:
                professionalism_scores.append(
                    analysis.professionalism_score
                )

            if analysis.empathy_score is not None:
                empathy_scores.append(
                    analysis.empathy_score
                )

            # -----------------------------------------------------
            # Sentiment
            # -----------------------------------------------------

            sentiment = (
                (analysis.sentiment or "")
                .strip()
                .lower()
            )

            if sentiment == "positive":
                positive += 1
            elif sentiment == "neutral":
                neutral += 1
            elif sentiment == "negative":
                negative += 1
            else:
                other += 1

            # -----------------------------------------------------
            # Greeting / Closing
            # -----------------------------------------------------

            if analysis.greeting_followed:
                greeting_followed += 1
            else:
                greeting_not_followed += 1

            if analysis.closing_followed:
                closing_followed += 1
            else:
                closing_not_followed += 1

            # -----------------------------------------------------
            # Violations
            # -----------------------------------------------------

            violations = analysis.violations or ""

            if ReportService.has_violation(violations):
                violation_counter[
                    violations.strip()
                ] += 1

            # -----------------------------------------------------
            # Daily performance
            # -----------------------------------------------------

            report_date = (
                media.created_at.date()
                if media.created_at
                else None
            )

            if report_date:
                day = daily_data[report_date]

                day["calls"] += 1

                if analysis.overall_score is not None:
                    day["overall_scores"].append(
                        analysis.overall_score
                    )

                if analysis.compliance_score is not None:
                    day["compliance_scores"].append(
                        analysis.compliance_score
                    )

                if analysis.professionalism_score is not None:
                    day["professionalism_scores"].append(
                        analysis.professionalism_score
                    )

                if analysis.empathy_score is not None:
                    day["empathy_scores"].append(
                        analysis.empathy_score
                    )

                if ReportService.has_violation(violations):
                    day["violations"] += 1

            # -----------------------------------------------------
            # Calling Agent Performance
            # -----------------------------------------------------

            # IMPORTANT:
            # Only actual calling agents are included.
            #
            # We use Media.calling_agent_id through the joined
            # `agent` object.
            #
            # Org Admin / Team Lead will NOT appear unless they
            # actually handled a call.

            if agent is not None:

                agent_key = agent.id

                current_agent = agent_data[agent_key]

                current_agent["agent_id"] = agent.id
                current_agent["agent_name"] = agent.full_name

                if org:
                    current_agent["organization_id"] = org.id
                    current_agent["organization_name"] = org.name

                if current_team:
                    current_agent["team_id"] = current_team.id
                    current_agent["team_name"] = current_team.name

                current_agent["calls"] += 1

                if analysis.overall_score is not None:
                    current_agent["overall_scores"].append(
                        analysis.overall_score
                    )

                if analysis.compliance_score is not None:
                    current_agent["compliance_scores"].append(
                        analysis.compliance_score
                    )

                if analysis.professionalism_score is not None:
                    current_agent["professionalism_scores"].append(
                        analysis.professionalism_score
                    )

                if analysis.empathy_score is not None:
                    current_agent["empathy_scores"].append(
                        analysis.empathy_score
                    )

                if ReportService.has_violation(violations):
                    current_agent["violations"] += 1

        # ---------------------------------------------------------
        # DAILY PERFORMANCE
        # ---------------------------------------------------------

        daily_performance = []

        for report_date in sorted(daily_data):

            day = daily_data[report_date]

            daily_performance.append(
                {
                    "date": report_date,
                    "calls": day["calls"],
                    "average_overall_score": average(
                        day["overall_scores"]
                    ),
                    "average_compliance": average(
                        day["compliance_scores"]
                    ),
                    "average_professionalism": average(
                        day["professionalism_scores"]
                    ),
                    "average_empathy": average(
                        day["empathy_scores"]
                    ),
                    "violations": day["violations"],
                }
            )

        # ---------------------------------------------------------
        # AGENT PERFORMANCE
        # ---------------------------------------------------------

        agent_performance = []

        for data in agent_data.values():

            agent_performance.append(
                {
                    "agent_id": data["agent_id"],
                    "agent_name": data["agent_name"],
                    "organization_id": data["organization_id"],
                    "organization_name": data["organization_name"],
                    "team_id": data["team_id"],
                    "team_name": data["team_name"],
                    "calls": data["calls"],
                    "average_overall_score": average(
                        data["overall_scores"]
                    ),
                    "average_compliance": average(
                        data["compliance_scores"]
                    ),
                    "average_professionalism": average(
                        data["professionalism_scores"]
                    ),
                    "average_empathy": average(
                        data["empathy_scores"]
                    ),
                    "violations": data["violations"],
                }
            )

        # Highest-performing calling agents first
        agent_performance.sort(
            key=lambda item: item[
                "average_overall_score"
            ],
            reverse=True,
        )

        # ---------------------------------------------------------
        # FINAL REPORT
        # ---------------------------------------------------------

        return {
            "organization": {
                "id": organization.id if organization else None,
                "name": organization.name if organization else None,
            },

            "team": {
                "id": team.id if team else None,
                "name": team.name if team else None,
            },

            "report_period": {
                "start_date": start_date,
                "end_date": end_date,
            },

            "summary": {
                "total_calls": total_calls,
                "analyzed_calls": total_calls,
                "average_overall_score": average(
                    overall_scores
                ),
                "average_compliance": average(
                    compliance_scores
                ),
                "average_professionalism": average(
                    professionalism_scores
                ),
                "average_empathy": average(
                    empathy_scores
                ),
            },

            "sentiment": {
                "positive": positive,
                "neutral": neutral,
                "negative": negative,
                "other": other,
            },

            "rules": {
                "greeting_followed": greeting_followed,
                "greeting_not_followed": greeting_not_followed,
                "closing_followed": closing_followed,
                "closing_not_followed": closing_not_followed,
            },

            "violations": [
                {
                    "violation": violation,
                    "count": count,
                }
                for violation, count
                in violation_counter.most_common()
            ],

            "daily_performance": daily_performance,

            "agent_performance": agent_performance,
        }