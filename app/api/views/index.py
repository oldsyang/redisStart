import datetime
import random

import aioredis
from databases import Database
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, select

from api.models import User
from api.schemas import UserRegisterFake, UserSignForMonthRequest, UserSignRequest
from common.constants import DATE_NEW_KEY, INTER_KEY, NEW_KEY, TOTAL_KEY, fake as faker
from common.redis import get_redis
from utils import response_code
from utils.tools import iter_items, now_time

router = APIRouter()


@router.get("/heart/", summary="心跳")
async def heart(request: Request):
    """:arg"""

    return response_code.resp_200({})


@router.get("/user/count", summary="获取当天用户新增数和总用户数")
async def get_user_cn(request: Request):
    """:arg"""
    redis: aioredis.Redis = await get_redis()
    await redis.execute_command("select", 3)
    now = now_time().strftime("%Y%m%d")
    date_new_key = DATE_NEW_KEY.format(date=now)

    # 计算日期与累计用户的差集
    """
    Set 的差集、并集和交集的计算复杂度较高，在数据量较大的情况下，如果直接执行这些计算，会导致 Redis 实例阻塞。建议：
    1. 你可以从主从集群中选择一个从库，让它专门负责聚合计算，
    2. 或者是把数据读取到客户端，在客户端来完成聚合统计，这样就可以规避阻塞主库实例和其他从库实例的风险了。
    """
    new_data = await redis.sdiffstore(NEW_KEY, date_new_key, TOTAL_KEY)
    total = await redis.scard(TOTAL_KEY)

    return response_code.resp_200({"new_data": new_data, "total": total + new_data})


@router.get("/user/retention", summary="获取今日的留存（上一天与当前的交集）")
async def get_retention(request: Request):
    """
    当要计算 7 月 3 日的留存用户时，我们只需要再计算 user:id:20210703 和 user:id:20210704 两个 Set 的交集，就可以得到同时在这两个集合中的用户 ID 了，
    这些就是在 7 月 3 日登录，并且在 7 月 4 日留存的用户。执行的命令如下：
    SINTERSTORE user:id:inter user:id:20210703 user:id:20210704
    Args:
        request:

    Returns:

    """
    redis: aioredis.Redis = await get_redis()
    await redis.execute_command("select", 3)
    now = now_time()
    today_key = DATE_NEW_KEY.format(date=now.strftime("%Y%m%d"))
    yesterday_key = DATE_NEW_KEY.format(date=(now + datetime.timedelta(days=-1)).strftime("%Y%m%d"))
    data = await redis.sinterstore(INTER_KEY, today_key, yesterday_key)
    return response_code.resp_200({"val": data})


@router.get("/user/sign", summary="检查用户某日的签到情况")
async def get_user_sign_for_day(request: Request, params: UserSignRequest = Depends(UserSignRequest.as_params)):
    """
    GETBIT uid:sign:28762:202107 4
    Args:
        request:

    Returns:

    """
    redis: aioredis.Redis = await get_redis()
    await redis.execute_command("select", 3)
    key = "user:sign:{}:{}".format(params.user_id, params.date[:6])
    data = await redis.getbit(key, int(params.date[-2:]))
    return response_code.resp_200({"val": data})


@router.get("/user/sign/month", summary="检查用户某月的签到次数")
async def get_user_sign_for_month(request: Request,
                                  params: UserSignForMonthRequest = Depends(UserSignForMonthRequest.as_params)):
    """
    BITCOUNT uid:sign:28762:202007
    Args:
        request:

    Returns:

    """

    redis: aioredis.Redis = await get_redis()
    await redis.execute_command("select", 3)
    key = "user:sign:{}:{}".format(params.user_id, params.date[:6])
    data = await redis.bitcount(key)
    return response_code.resp_200({"val": data})


@router.get("/user/sign/continuous", summary="统计连续签到的用户数")
async def get_user_sign_continue_count(request: Request):
    """
    BITCOUNT uid:sign:28762:202007
    Args:
        request:

    Returns:

    """

    redis: aioredis.Redis = await get_redis()
    await redis.execute_command("select", 3)
    now = now_time().date()
    key = "user:sign:{date}"

    keys = [
        key.format(date=(now + datetime.timedelta(days=i)).strftime("%Y%m%d"))
        for i in range(-4, 0)
    ]

    await redis.bitop("and", "user:sign:and", *keys)
    data = await redis.bitcount("user:sign:and")
    return response_code.resp_200({"val": data})


@router.get("/page/uv", summary="统计页面的uv")
async def get_page_uv(request: Request, page: str = Query(..., title="页面")):
    """
    这里的基数统计，存在一个问题，是有一定误差的
    pfcount page1:uv
    Args:
        page:
        request:

    Returns:

    """

    redis: aioredis.Redis = await get_redis()
    await redis.execute_command("select", 3)
    key = f"page:{page}:uv"
    val = await redis.pfcount(key)
    return response_code.resp_200({"val": val})


@router.post("/user/data", summary="增加每天用户登录模拟数据")
async def post_user_data_per_day(request: Request, fake: UserRegisterFake = Depends(UserRegisterFake.as_params)):
    redis = await get_redis()
    await redis.execute_command("select", 3)
    db: Database = request.app.state.db

    # 此处我简单的去数据库取一下数据（并非实际业务）
    result = await db.fetch_one(
        select([func.max(User.id)]).select_from(User)
    )
    last_id = result[0] + 1 if all(result) else 1
    incr_total = random.randrange(100, 200)
    new_user_ids = last_id + incr_total + 1
    date_new_key = DATE_NEW_KEY.format(date=fake.date)

    # 模拟注册数量
    new_ids = [u_id for u_id in range(last_id, new_user_ids)]

    created_at = datetime.datetime.strptime(fake.date, "%Y%m%d")
    async with db.transaction() as conn:
        await db.execute_many(
            query=User.__table__.insert(),
            values=[
                {'id': _u_id, "created_at": created_at, "nick_name": faker.name()}
                for _u_id in new_ids
            ]
        )

    old_ids = await User.random_user(db, created_at=created_at)

    new_ids = list(set(new_ids) | {i[0] for i in old_ids})

    for ids in iter_items(new_ids, 100):
        await redis.sadd(date_new_key, *ids)

    return response_code.resp_200({})
