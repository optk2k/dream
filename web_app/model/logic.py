import httpx
from sqlalchemy import desc, insert, select
from .table_badlisted_words import BadlistedWords
from .table_spacy_nounphrases import SpacyNounphrases
from .connection import async_session, badlisted_words, spacy_nounphrases


def request_format(string: str) -> dict[str, list[str]]:
    return {"sentences": [string]}


async def request_processing(url: str, data_request: str):
    """Делаем запрос к сервису."""

    request: dict[str, list[str]] = request_format(data_request)
    async with httpx.AsyncClient() as client:
        result = await client.post(
            url,
            json=request,
            timeout=30,
            follow_redirects=True,
        )
    return result


async def get_badlisted_words():
    """Вытаскиваем из базы последние записи badlisted_words."""
    async with async_session() as session:
        stmt = select(BadlistedWords).order_by(desc(column=BadlistedWords.id)).limit(30)
        result = await session.execute(stmt)
        return result.scalars()


async def get_spacy_nounphrases():
    """Вытаскиваем из базы последние записи spacy_nounphrases."""
    async with async_session() as session:
        stmt = (
            select(SpacyNounphrases)
            .order_by(desc(column=SpacyNounphrases.id))
            .limit(30)
        )
        result = await session.execute(stmt)
        return result.scalars()


async def request_and_save_badlisted_words(text: str):
    """Сделать запрос к сервису badlisted_words и сохранить его в базе."""
    if text != "":
        processing_text = await request_processing(
            url=badlisted_words, data_request=text
        )

        async with async_session() as session:
            stmt = insert(BadlistedWords).values(
                request=text, response=processing_text.json()[0]["bad_words"]
            )
            await session.execute(stmt)
            await session.commit()

    return await get_badlisted_words()


async def request_and_save_spacy_nounphrases(text: str):
    """Сделать запрос к сервису spacy_nounphrases и сохранить его в базе."""
    if text != "":
        processing_text = await request_processing(
            url=spacy_nounphrases, data_request=text
        )
        async with async_session() as session:
            stmt = insert(SpacyNounphrases).values(
                request=text, response="; ".join(processing_text.json()[0])
            )
            await session.execute(stmt)
            await session.commit()

    return await get_spacy_nounphrases()
