from datetime import datetime

import pytz
from sqlalchemy import MetaData, create_engine
from sqlalchemy import select, update
from decouple import config



name =  config('DB_NAME')
user = config('DB_USER')
password = config('DB_PASSWORD')
host = config('DB_HOST')
port = config('DB_PORT', cast=int)



class MyDatabase:
    def __init__(self, engine, single, order, recvisity):
        self.engine = engine
        self.single = single
        self.order = order
        self.recvisity = recvisity

    def create_order(self, price, user_id, region, good_id, order_id, link, username, status='waiting'):
        bishkek_tz = pytz.timezone("Asia/Bishkek")
        payload = {
            "price": price,
            "user_id": user_id,
            "username": username,
            "region": region,
            "good_id": good_id,
            "order_id": order_id,
            "link": link,
            "status": status,
            "created_at": datetime.now(tz=bishkek_tz)
        }
        with self.engine.connect() as conn:
            das = conn.execute(self.order.insert(),
                         payload
                         )
            conn.commit()
            new_announce_id = das.inserted_primary_key[0]

            conn.commit()
            item = conn.execute(
                select(
                    self.order
                ).where(self.order.c.id == new_announce_id)
            )
            users = item.mappings().all()[0]
            return users

    def get_recvisits(self, region):
        with self.engine.connect() as conn:
            items = conn.execute(
                select(
                    self.recvisity
                )
                .where(self.recvisity.c.region == region)
            )
            items = items.mappings().all()
            return items

    def get_single(self):
        with self.engine.connect() as conn:
            items = conn.execute(
                select(
                    self.single
                )
            )
            items = items.mappings().all()
            return items[0]

    def update_order_status(self, order_id, new_status):
        """
        Обновляет статус заказа в таблице shop_order.

        :param order_id: ID заказа, статус которого нужно обновить.
        :param new_status: Новый статус для обновления.
        :return: Словарь с обновленным заказом.
        """
        with self.engine.connect() as conn:
            # Формируем запрос на обновление
            conn.execute(
                update(self.order)
                .where(self.order.c.id == order_id)
                .values(status=new_status)
            )
            conn.commit()

            # Извлекаем обновленный заказ для проверки
            updated_item = conn.execute(
                select(self.order).where(self.order.c.id == order_id)
            )
            updated_item = updated_item.mappings().all()
            if updated_item:
                return updated_item[0]
            else:
                return None


engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}/{name}')
meta = MetaData()

meta.reflect(bind=engine)

single = meta.tables['shop_singlemodel']
order = meta.tables['shop_order']
recvisity = meta.tables['shop_recvisity']

db = MyDatabase(engine=engine, single=single, order=order, recvisity=recvisity)

