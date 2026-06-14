from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.filters import FilterOptions
from app.services.cache import cached

SCHEMA = "warehouse"


@cached(ttl=300)
async def get_filters(db: AsyncSession, redis: Redis | None = None) -> FilterOptions:
    date_sql = text(f"""
        SELECT MIN(date)::text AS date_min, MAX(date)::text AS date_max
        FROM {SCHEMA}.dim_time
    """)
    types_sql = text(f"""
        SELECT DISTINCT primary_type
        FROM {SCHEMA}.fact_crime f
        JOIN {SCHEMA}.dim_offense o ON f.offense_id = o.offense_id
        WHERE primary_type IS NOT NULL
        ORDER BY primary_type
    """)
    dist_sql = text(f"""
        SELECT DISTINCT district
        FROM {SCHEMA}.dim_location
        WHERE district IS NOT NULL
        ORDER BY district
    """)
    ca_sql = text(f"""
        SELECT DISTINCT community_area
        FROM {SCHEMA}.dim_location
        WHERE community_area IS NOT NULL
        ORDER BY community_area
    """)

    date_result = await db.execute(date_sql)
    date_row = date_result.one()

    types_result = await db.execute(types_sql)
    types = [str(r.primary_type) for r in types_result.fetchall()]

    dist_result = await db.execute(dist_sql)
    districts = [int(r.district) for r in dist_result.fetchall()]

    ca_result = await db.execute(ca_sql)
    community_areas = [int(r.community_area) for r in ca_result.fetchall()]

    return FilterOptions(
        date_min=str(date_row.date_min),
        date_max=str(date_row.date_max),
        primary_types=types,
        districts=districts,
        community_areas=community_areas,
    )
