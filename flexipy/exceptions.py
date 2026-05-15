class FlexipyException(Exception):
    def __init__(
        self,
        message,
        status_code=None,
        message_code=None,
        response_json=None,
        response_text=None,
        url=None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.message_code = message_code
        self.response_json = response_json
        self.response_text = response_text
        self.url = url
