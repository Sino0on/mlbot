from sqlalchemy import MetaData, create_engine
from sqlalchemy import select
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

    def create_order(self, price, user_id, region, good_id, order_id, link, status='waiting'):
        payload = {
            "price": price,
            "user_id": user_id,
            "region": region,
            "good_id": good_id,
            "order_id": order_id,
            "link": link,
            "status": status,
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


engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}/{name}')
meta = MetaData()

meta.reflect(bind=engine)

single = meta.tables['shop_singlemodel']
order = meta.tables['shop_order']
recvisity = meta.tables['shop_recvisity']

db = MyDatabase(engine=engine, single=single, order=order, recvisity=recvisity)

