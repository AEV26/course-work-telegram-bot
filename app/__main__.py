import asyncio
from datetime import datetime
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from app.middlewares.menu_middleware import MenuMiddleware
from app.service.rent_object_service import RentObjectService
from app.settings.config import load_config
from app.middlewares.rent_object_service import RentObjectServiceMiddleware
from app.handlers import main_router

logging.basicConfig(
    format=(
        "%(asctime)s - [%(levelname)s] - %(name)s"
        "- (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
    ),
    level=logging.INFO,
    handlers=[
        logging.FileHandler(
            f"logs/logs_{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.log"
        ),
        logging.StreamHandler(),
    ],
)


def setup_middlewares(dp: Dispatcher):
    service_middleware = RentObjectServiceMiddleware(
        RentObjectService("http://localhost:8080")
    )
    menu_middleware = MenuMiddleware()

    dp.message.middleware(service_middleware)
    dp.callback_query.middleware(service_middleware)

    dp.message.middleware(menu_middleware)
    dp.callback_query.middleware(menu_middleware)


def setup_routers(dp: Dispatcher):
    dp.include_routers(main_router)


async def main():
    config = load_config()
    bot = Bot(config.bot.token, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=RedisStorage.from_url(config.redis.url))

    setup_middlewares(dp)
    setup_routers(dp)

    try:
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()


if __name__ == "__main__":
    asyncio.run(main())
