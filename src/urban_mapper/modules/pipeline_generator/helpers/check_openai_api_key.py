import os


def check_openai_api_key(func):
    def wrapper(self, *args, **kwargs):
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError(
                "OpenAI API key is not set. Please set the 'OPENAI_API_KEY' environment variable.\n"
                "You can obtain an API key from https://platform.openai.com/account/api-keys.\n"
                "Example: export OPENAI_API_KEY='your-api-key-here'"
            )
        return func(self, *args, **kwargs)

    return wrapper
