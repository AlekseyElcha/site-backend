from pydantic import BaseModel

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

    question_created_message_to_admins: str = (
        "Было создано новое обращение на платформе.\n"
        "Ссылка на обращение: localhost:3000/admins/{unique_id}\n\n"
        "Базовая информация об обращении:\n"
        "{question_data}"
    )

    extra_message_created_notification_to_admins: str = (
        "Было отправлено новое дополнительное сообщение к обращению {question_id}.\n\n"
        "Ознакомится по ссылке: localhost:3000/admins/{unique_id}\n\n"
        "Базовая информация о сообщении:\n"
        "{message_data}"
    )

    def format_message_text(self, name: str, surname: str, unique_id: str) -> str:
        return self.question_created_message_template.format(
            name=name,
            surname=surname,
            unique_id=unique_id
        )

    def format_message_text_for_admins(self, unique_id: str, question_data: dict) -> str:
        return self.question_created_message_to_admins.format(
            unique_id=unique_id,
            question_data=question_data
        )

    def format_extra_message_text(self, unique_id: str, message_data: dict) -> str:
        return self.extra_message_created_notification_to_admins.format(
            unique_id=unique_id,
            message_data=message_data
        )
