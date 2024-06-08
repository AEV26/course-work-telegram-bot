from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv
import os


PATH_TO_ROOT = Path(__file__).parent.parent.parent


@dataclass
class BotConfig:
    token: str


@dataclass
class RedisConfig:
    """RedisStorage config"""

    host: str
    port: str
    db: str
    user: str
    password: str

    @property
    def url(self) -> str:
        if self.user == "":
            return f"redis://{self.host}:{self.port}/{self.db}"

        if self.password == "":
            return f"redis://{self.user}@{self.host}:{self.port}/{self.db}"

        return f"redis://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


@dataclass
class Config:
    """Configurator"""

    bot: BotConfig
    redis: RedisConfig


def load_config() -> Config:
    load_dotenv()

    config = Config(
        bot=BotConfig(token=os.environ["BOT_TOKEN"]),
        redis=RedisConfig(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=os.getenv("REDIS_PORT", "6309"),
            db=os.getenv("REDIS_DB", "0"),
            user=os.getenv("REDIS_USER", ""),
            password=os.getenv("REDIS_PASSWORD", ""),
        ),
    )
    return config
