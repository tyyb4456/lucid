from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""
    LUCID_NAME: str = "Lucid"
    LUCID_VOICE_ENABLED: bool = True
    LUCID_WAKE_WORD: str = "lucid"
    TODO_FILE_PATH: str = "./data/todos/todos.json"
    NOTES_FILE_PATH: str = "./data/notes/notes.json"
    SCREENSHOTS_DIR: str = "./data/screenshots"

    class Config:
        env_file = ".env"

settings = Settings()