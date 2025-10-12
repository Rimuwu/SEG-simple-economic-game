from global_modules.logs import Logger


nostream_logger = Logger()
nostream_logger.disable_console_output()

routers_logger = nostream_logger.get_logger("routers")
websocket_logger = nostream_logger.get_logger("websocket")

game_logger = Logger().get_logger("game")