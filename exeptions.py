class QuestionsBaseException(BaseException):
    pass


class CreateNewQuestionError(QuestionsBaseException):
    pass


class GetAllQuestionsListError(QuestionsBaseException):
    pass


class CreateNewAnswerError(QuestionsBaseException):
    pass


class GetUserEmailByQuestionError(QuestionsBaseException):
    pass


class GetUserEmailByQuestionErrorInEmailSender(QuestionsBaseException):
    pass


class SendEmailError(QuestionsBaseException):
    pass


class UpdateQuestionStatusError(QuestionsBaseException):
    pass

