from pydantic import BaseModel

from src.schemas.schemas import NewQuestionSchema


class Business(BaseModel):
    email_code_verification_timeout_minutes: int = 15

    question_created_message_template: str = (
        "Уважаемый {name} {surname},\n"
        "Уведомляем Вас о том, что Вы успешно создали обращение в ООО «Домофон-сервис» "
        "при помощи нашего онлайн-сервиса <ССЫЛКУ СЮДА> \n\n"
        "Если Вы не оставляли обращение, напишите <СЮДА> - со всем разберёмся.\n"
        "Уникальный идентификатор вопроса: {unique_id}\n\n"
        "Данное письмо было отправлено автоматически, просьба не отвечать на него."
    )

    def format_message_text(self, name: str, surname: str, unique_id: str) -> str:
        return self.question_created_message_template.format(
            name=name,
            surname=surname,
            unique_id=unique_id
        )
