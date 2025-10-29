class Message:
    def __init__(self, isError: bool, text: str):
        self.isError = isError
        self.text = text

    @staticmethod
    def NewMessage(isError: bool, text: str) -> 'Message':
        return Message(isError, text)
