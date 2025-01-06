from dagster import Definitions, load_assets_from_modules

import mental_health_assets

all_assets = load_assets_from_modules([mental_health_assets])

defs = Definitions(
    assets=all_assets,
)
