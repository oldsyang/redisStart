import asyncio
import datetime
import random

from databases import Database
from sqlalchemy import Column, String, func, select

from api.models.base import BaseModel
from common.constants import DATE_NEW_KEY, TOTAL_KEY, fake as faker
from common.database import AioDB
from common.redis import get_redis
from utils.tools import iter_items, now_time


class User(BaseModel):
    """用户表"""
    __table_args__ = {'extend_existing': True}
    nick_name = Column(String(31), comment="昵称")

    @classmethod
    async def random_user(cls, db: Database, cn=1, created_at=None):
        """
        随机一定数量的用户
        Args:
            db:
            cn:
            created_at:

        Returns:

        """
        # 随机一部分用户出来，登录
        if not created_at:
            created_at = now_time()
        user_cn = await db.fetch_one(
            select([func.count()]).select_from(User).where(User.created_at <= created_at)
        )

        user_cn = user_cn[0] if all(user_cn) else 0
        if not user_cn:
            return []
        rank_offset = random.randrange(0, user_cn)
        # 模拟登录数据
        rank_limit = cn or random.randrange(1, max(user_cn - rank_offset, 2))

        old_ids = await db.fetch_all(
            select([User.id]).select_from(User).where(User.created_at <= created_at).limit(rank_limit).offset(
                rank_offset)
        )
        return old_ids if all(old_ids) else []

    @classmethod
    async def rank_user(cls, db: Database) -> int:
        count = await db.fetch_one(
            select([func.count()]).select_from(User)
        )
        if not all(count):
            return 0
        user_cn = count[0]
        rank_offset = random.randrange(1, user_cn)
        result = await db.fetch_one(
            select([User.id]).select_from(User).limit(1).offset(rank_offset)
        )
        return result[0] if result else 0

    @classmethod
    async def sign(cls):
        """
        签到场景数据模拟

        记录签到（1）或未签到（0），这是一种典型的二值状态统计，可使用Bitmap这种数据类型，他是按位占坑，空间使用非常紧凑

        Returns:

        """
        now = now_time().date()
        async with AioDB() as db:
            user_ids = await User.random_user(db)
            if not user_ids:
                return
            user_id = user_ids[0]

        key = "user:sign:{u_id}".format(u_id=user_id)
        key += ":{date}"
        redis = await get_redis()
        await redis.execute_command("select", 3)
        for i in range(-4, 5):  # 模拟前后5天的打卡情况
            date = now + datetime.timedelta(days=i)
            main_key = key.format(date=date.strftime("%Y%m"))
            await redis.setbit(main_key, date.day, random.randrange(0, 2))

    @classmethod
    async def page_uv(cls):
        """
        统计页面的uv情况模拟

        1.优先想到的可以是要去重的数据结构，set或者hash，但是随着页面和用户数量的增加，性能会受到恨到影响
        2.这里Redis有一个天然的基于基数统计的类型：HyperLogLog
        在 Redis 中，每个 HyperLogLog 只需要花费 12 KB 内存，就可以计算接近 2^64 个元素的基数。HyperLogLog 非常节省空间。
        Returns:

        """
        async with AioDB() as db:
            user_ids = await User.random_user(db, cn=0)
            if not user_ids:
                return

            user_ids = [i[0] for i in user_ids]

        redis = await get_redis()
        await redis.execute_command("select", 3)
        for ids in iter_items(user_ids, 50):
            await redis.pfadd("page:index:uv", *ids)

    @classmethod
    async def sign_pro(cls):
        """
        签到场景数据模拟，模拟所有用户的连续签到情况，如1万用户，连续3天的签到情况

        可以用时间作为key，用户id用来占位
        Returns:

        """
        now = now_time().date()
        async with AioDB() as db:  # 注意这里是模拟数据，实际业务场景请勿这么查询数据量
            result = await db.fetch_all(
                select([User.id]).select_from(User)
            )

        key = "user:sign:{date}"
        redis = await get_redis()
        await redis.execute_command("select", 3)
        for i in range(-4, 0):  # 模拟前后5天的打卡情况
            date = now + datetime.timedelta(days=i)
            main_key = key.format(date=date.strftime("%Y%m%d"))
            for u_id in result:
                await redis.setbit(main_key, u_id[0], random.randrange(0, 2))

    @classmethod
    async def total_user(cls):
        """
            这里模拟定时器，每日聚合
        Returns:

        """
        now = now_time().date().strftime('%Y%m%d')
        async with AioDB() as db:
            result = await db.fetch_all(
                select([func.date_format(User.created_at, "%Y%m%d")]).select_from(User).where(
                    User.created_at < now
                ).group_by(
                    func.date_format(User.created_at, "%Y%m%d")
                )
            )

            result = [DATE_NEW_KEY.format(date=i[0]) for i in result] if result else []

        redis = await get_redis()
        await redis.execute_command("select", 3)
        for dates in iter_items(result, 10):
            await redis.sunionstore(TOTAL_KEY, TOTAL_KEY, *dates)

    @classmethod
    async def rank_register_or_login(cls):
        """模拟每天用户的登录情况"""
        now = now_time()
        is_register = random.randrange(0, 2)

        async with AioDB() as db:
            if is_register:
                result = await db.execute(
                    query=User.__table__.insert(),
                    values={"created_at": now, "nick_name": faker.name()}
                )
            else:
                # 随机一条数据
                user_ids = await User.random_user(db)
                if not user_ids:
                    return
                result = user_ids[0]

        redis = await get_redis()
        await redis.execute_command("select", 3)
        await redis.sadd(DATE_NEW_KEY.format(date=now.strftime("%Y%m%d")), result)
        return result


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(User.page_uv())
    loop.run_until_complete(future)
    print(future.result())
