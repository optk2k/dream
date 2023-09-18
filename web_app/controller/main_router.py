from typing import Any
from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates
from model.logic import (
    request_and_save_badlisted_words,
    get_badlisted_words,
    request_and_save_spacy_nounphrases,
    get_spacy_nounphrases,
)
from fastapi.responses import RedirectResponse


main_router = APIRouter(prefix="", tags=["main"])

templates: Any = Jinja2Templates(directory="view")


@main_router.get("/")
async def start(request: Request):
    return RedirectResponse("/badlisted_words")


@main_router.get("/badlisted_words")
async def badlisted_words_view(request: Request) -> dict[str, str]:
    records = await get_badlisted_words()
    return templates.TemplateResponse(
        "badlisted_words.html", {"request": request, "records": records}
    )


@main_router.post("/badlisted_words")
async def badlisted_words_processing(
    request: Request, text: str = Form("")
) -> dict[str, str]:
    records = await request_and_save_badlisted_words(text)

    return templates.TemplateResponse(
        "badlisted_words.html", {"request": request, "records": records}
    )


@main_router.get("/spacy_nounphrases")
async def spacy_nounphrases_view(request: Request) -> dict[str, str]:
    records = await get_spacy_nounphrases()
    return templates.TemplateResponse(
        "spacy_nounphrases.html", {"request": request, "records": records}
    )


@main_router.post("/spacy_nounphrases")
async def spacy_nounphrases_processing(
    request: Request, text: str = Form("")
) -> dict[str, str]:
    records = await request_and_save_spacy_nounphrases(text)

    return templates.TemplateResponse(
        "spacy_nounphrases.html", {"request": request, "records": records}
    )
