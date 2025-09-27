from oms_dir import scene_manager
from bot_instance import dp
from aiogram.filters import Command
from aiogram.types import Message
from scenes.game_scenario import GameManger

@dp.message(Command('test'))
async def test(message: Message):
    scene = scene_manager.create_scene(
        message.from_user.id,
        GameManger
    )
    await scene.start()