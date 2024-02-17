from database.models import Location, Role, GameState

import json
import aiofiles


async def add_locations():
    async with aiofiles.open("./data/locations.json", "r") as f:
        deserialized_fixtures = await f.read()
        serialized_fixtures = json.loads(deserialized_fixtures)
        locations = []
        for name in serialized_fixtures:
            locations.append(Location(name=name))
        await Location.add_many(locations)


async def add_roles():
    async with aiofiles.open("./data/roles.json", "r") as f:
        deserialized_fixtures = await f.read()
        serialized_fixtures = json.loads(deserialized_fixtures)
        roles = []
        for _id, name in serialized_fixtures.items():
            roles.append(Role(id=int(_id), name=name))
        await Role.add_many(roles)


async def add_game_states():
    async with aiofiles.open("./data/game_states.json", "r") as f:
        deserialized_fixtures = await f.read()
        serialized_fixtures = json.loads(deserialized_fixtures)
        game_states = []
        for _id, name in serialized_fixtures.items():
            game_states.append(GameState(id=int(_id), name=name))
        await GameState.add_many(game_states)


async def load_fixtures():
    if not await Location.has_fixtures():
        await add_locations()
    if not await Role.has_fixtures():
        await add_roles()
    if not await GameState.has_fixtures():
        await add_game_states()
