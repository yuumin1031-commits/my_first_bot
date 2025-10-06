import peewee
from datetime import datetime

# データベースの接続設定（SQLiteの場合）
db = peewee.SqliteDatabase("bulletin_board.db")


# モデルの定義
class BaseModel(peewee.Model):
    class Meta:
        database = db


# ユーザーモデル
class User(BaseModel):
    user_id = peewee.CharField(unique=True)
    is_admin = peewee.BooleanField(default=False)


# 回覧板モデル
class Bulletin(BaseModel):
    title = peewee.CharField()
    content = peewee.TextField()
    created_at = peewee.DateTimeField(default=datetime.now)


# データベースの初期化
def initialize_db():
    db.connect()
    db.create_tables([User, Bulletin])
    db.close()


if __name__ == "__main__":
    initialize_db()
