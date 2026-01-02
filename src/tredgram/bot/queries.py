from __future__ import annotations

import asyncio
import io
import logging
import logging.config
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
from sqlalchemy import select

from db import QAModel, session_maker

logging.config.fileConfig("logconfig.ini")
logger = logging.getLogger("virtual_assistant")


async def get_custom_statistics() -> None:
    logger.info("Report generation started")
    async with session_maker() as db:
        now = datetime.now(ZoneInfo("Europe/Moscow")).replace(tzinfo=None)
        start_day = datetime(year=now.year, month=now.month, day=23, hour=9, minute=0, second=0)
        logger.info(start_day)

        # Last's day question and answers
        qas = await db.scalars(
            select(QAModel).where(
                (QAModel.sended_at >= start_day) & (QAModel.sended_at < now),
            ),
        )

        qas_array = [(qa.question, qa.answer) for qa in qas.all()]
        df_qas = pd.DataFrame(qas_array, columns=["Вопросы", "Ответы"])
        with pd.ExcelWriter("Статистика.xlsx", mode="w") as writer:
            df_qas.to_excel(writer, index=False)


if __name__ == "__main__":
    asyncio.run(get_custom_statistics())
