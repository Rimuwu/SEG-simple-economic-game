from oms import scene_manager
from bot_instance import dp, bot
from aiogram.filters import Command
from aiogram.types import Message
from scenes.game_scenario import GameManager

@dp.message(Command('start'))
async def test(message: Message):
    scene = scene_manager.create_scene(
        message.from_user.id,
        GameManager,
        bot
    )
    await scene.start()