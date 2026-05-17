from pydantic import BaseModel

class Business(BaseModel):
    email_code_verification_timeout_minutes: int = 15

    send_answer_email_mod_subject: str = f"ООО «Домофон-сервис». Ответ на Ваш вопрос."
    send_auth_code_subject: str = f"Ваш код для входа на сайт."

    question_created_message_template: str = (
        "Уважаемый {name} {surname},\n"
        "Уведомляем Вас о том, что Вы успешно создали обращение в ООО «Домофон-сервис» "
        "при помощи нашего онлайн-сервиса ask.domofon-servis-odi.ru \n\n"
        "Уникальный идентификатор вопроса: {unique_id}\n\n"
        "Данное письмо было отправлено автоматически, просьба не отвечать на него."
    )

    question_created_message_to_admins: str = (
        "Было создано новое обращение на платформе.\n"
        "Ссылка на обращение: ask.domofon-servis-odi.ru/admins/{unique_id}\n\n"
        "Базовая информация об обращении:\n"
        "{question_data}"
    )

    extra_message_created_notification_to_admins: str = (
        "Было отправлено новое дополнительное сообщение к обращению {question_id}.\n\n"
        "Ознакомится по ссылке: ask.domofon-servis-odi.ru/admins/{unique_id}\n\n"
        "Базовая информация о сообщении:\n"
        "{message_data}"
    )

    auth_code_generated_message: str = (
        "Ваш код для входа на сайт: {auth_code}\n"
        "Код действителен в течение {exp_time} минут.\n\n"
        "Данное письмо было отправлено автоматически."
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

    def format_auth_code_message(self, auth_code: str, exp_time: int) -> str:
        return self.auth_code_generated_message.format(
            auth_code=auth_code,
            exp_time=exp_time
        )
