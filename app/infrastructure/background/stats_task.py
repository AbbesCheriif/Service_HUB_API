from uuid import UUID

from fastapi import BackgroundTasks

from app.core.logging.logger import get_logger

logger = get_logger(__name__)


def schedule_provider_stats_recalculation(
    provider_id: UUID,
    background_tasks: BackgroundTasks,
) -> None:
    background_tasks.add_task(_recalculate_provider_stats, provider_id)


def _recalculate_provider_stats(provider_id: UUID) -> None:
    logger.info(
        "provider_stats_recalculation_triggered",
        provider_id=str(provider_id),
    )
