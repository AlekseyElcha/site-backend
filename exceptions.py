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


class CreateNewEmailVerificationCodeError(QuestionsBaseException):
    pass


class AddNewEmailVerificationCodeToDBError(QuestionsBaseException):
    pass


class BasicOperationDatabaseError(QuestionsBaseException):
    pass


class TokenHasExpired(QuestionsBaseException):
    pass


class TokenAlreadyUsed(QuestionsBaseException):
    pass


class DecodeTokenError(QuestionsBaseException):
    pass


class S3OperationsError(QuestionsBaseException):
    pass


class S3GetAllFilesError(QuestionsBaseException):\
    pass