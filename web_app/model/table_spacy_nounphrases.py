# spacy_nounphrases
from model.connection import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class SpacyNounphrases(Base):
    __tablename__ = "spacy_nounphrases"

    id: Mapped[int] = mapped_column(primary_key=True)
    request: Mapped[str]
    response: Mapped[str]

    def __str__(self):
        return f"id: {self.id},\
            request: {self.request[:30]},\
            response: {self.response[:30]}"
