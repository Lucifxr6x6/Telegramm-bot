from database.models import *
from telebot.types import Message
from loguru import logger
from config_data import config


def add_user(message: Message) -> None:
    """
    Создает базу данных если её еще нет, таблицу с данными пользователей:
    id, username и, если есть, "имя фамилия" и добавляет туда данные, если
    бота запускает новый пользователь. Данная таблица не участвует в выдаче сохраненной
    информации. Она просто хранит данные пользователя.
    : param message : Message
    : return : None
    """
    db.connect(config.DB_NAME)
    try:
        query = User.insert(
            chat_id=message.chat.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name)

        query.execute()

        logger.info(f'Добавлен новый пользователь. User_id: {message.chat.id}')
        db.commit()
    except peewee.IntegrityError:
        logger.info(f'Данный пользователь уже существует. User_id: {message.chat.id}')
    db.close()


def add_query(query_data: dict) -> None:
    """
    Создаёт таблицу, если она ещё не создавалась и добавляет туда данные,
    которые ввел пользователь для поиска
    : param query_data : dict
    : return : None
    """
    user_id = query_data['chat_id']
    db.connect(config.DB_NAME)
    try:
        res = Query.insert(user_id=query_data['chat_id'],
                           input_city=query_data['input_city'],
                           photo_need=query_data['photo_need'],
                           destination_id=query_data['destination_id'],
                           date_time=query_data['date_time'])
        print(res)
        res.execute()
        logger.info(f'В БД добавлен новый запрос. User_id: {user_id}')
        db.commit()
        # Нам не нужно очень много записей историй поиска, поэтому для каждого пользователя
        # будем хранить только 5 последних записей, лишние - удалим.
        source = (Query.select(Query.date_time).where(Query.user_id == user_id))
        source_2 = ((Query.select(fn.COUNT()).where(Query.user_id == user_id)) > 5)
        query = Query.delete().where(Query.date_time == source and source_2)
        query.execute()
        db.commit()
    except peewee.IntegrityError:
        logger.info(f'Запрос с такой датой и временем уже существует. User_id: {user_id}')
    db.close()


def add_response(search_result: dict) -> None:
    """
    Создаёт таблицу, если она ещё не создавалась и добавляет туда данные,
    которые бот получил в результате запросов к серверу.
    : param search_result : dict
    : return : None
    """

    db.connect(config.DB_NAME)

    for item in search_result.items():
        query = Query.select(Query.id).where(Query.date_time == (item[1]['date_time'],))
        query.execute()
        for i in query:
            result = i
            res = Response.insert(query_id=result,
                                  hotel_id=item[0],
                                  name=item[1]['name'],
                                  address=item[1]['address'],
                                  price=item[1]['price'],
                                  distance=item[1]['distance'])
            print(res)
            res.execute()
            db.commit()
            logger.info(f'В БД добавлены данные отеля. User_id: {item[1]["user_id"]}')

        for link in item[1]['images']:
            res = Images.insert(hotel_id=item[0],
                                link=link)

            res.execute()
        logger.info(f'В БД добавлены ссылки на фотографии отеля. User_id: {item[1]["user_id"]}')
        db.commit()
    db.close()
