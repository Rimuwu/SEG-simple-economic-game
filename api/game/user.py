from modules.baseclass import BaseClass


class User(BaseClass):

    __tablename__ = "users"
    __unique_id__ = "user_id"

    user_id: int
    username: str

    def __init__(self): pass

    def create(self, user_id: int = 0, username: str = ""):
        self.user_id = user_id
        self.username = username

        self.save_to_base()
        self.reupdate()

        return self
