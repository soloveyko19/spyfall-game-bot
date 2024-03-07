import uuid
from config import conf
from typing import Optional, List, Sequence, Iterable

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Boolean,
    and_,
    select,
    delete,
    BigInteger,
    desc,
)
from sqlalchemy import func
from sqlalchemy.schema import DefaultClause


db_url = f"postgresql+asyncpg://{conf.DB_USERNAME}:{conf.DB_PASSWORD}@{conf.DB_HOST}:5432/telegram_bot"
engine = create_async_engine(url=db_url)
async_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger, index=True, nullable=False, unique=True)
    full_name = Column(String(200), nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    locale = Column(String(2), nullable=False, server_default="en")

    players = relationship("Player", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")

    @classmethod
    async def get(cls, tg_id: int = None, id: int = None) -> "User":
        if not tg_id and not id:
            raise ValueError("At least one argument must be provided")
        async with async_session() as session:
            query = select(User).filter()
            if id:
                query = query.filter(User.id == id)
            else:
                query = query.filter(User.tg_id == tg_id)
            res = await session.execute(query)
            return res.scalar_one_or_none()

    @classmethod
    async def get_admins(cls):
        async with async_session() as session:
            query = select(User).filter(User.is_admin == True)
            res = await session.execute(query)
            return res.scalars().all()

    @classmethod
    async def get_count(cls):
        async with async_session() as session:
            query = select(func.count()).select_from(User)
            res = await session.execute(query)
            return res.scalar()

    @classmethod
    async def get_all(cls) -> Iterable["User"]:
        async with async_session() as session:
            query = select(User).order_by(User.id)
            res = await session.execute(query)
            return res.scalars().all()

    async def save(self):
        async with async_session() as session:
            session.add(self)
            await session.commit()


class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(70), nullable=False)
    games = relationship("Game", back_populates="location")

    @classmethod
    async def get_random(cls) -> "Location":
        async with async_session() as session:
            query = select(Location).order_by(func.random()).limit(1)
            res = await session.execute(query)
            return res.scalar()

    @classmethod
    async def add_many(cls, instances: List["Location"]) -> List["Location"]:
        async with async_session() as session:
            session.add_all(instances)
            await session.commit()
            return instances

    @classmethod
    async def has_fixtures(cls) -> bool:
        async with async_session() as session:
            query = select(Location).limit(1)
            res = await session.execute(query)
            return bool(res.unique().scalar_one_or_none())

    @classmethod
    async def get_list(cls) -> Sequence["Location"]:
        async with async_session() as session:
            query = select(Location).order_by(Location.name)
            res = await session.execute(query)
            return res.scalars().all()


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(10), nullable=False)
    players = relationship("Player", back_populates="role")

    @classmethod
    async def add_many(cls, instances: List["Role"]) -> List["Role"]:
        async with async_session() as session:
            session.add_all(instances)
            await session.commit()
            return instances

    @classmethod
    async def has_fixtures(cls) -> bool:
        async with async_session() as session:
            query = select(Role).limit(1)
            res = await session.execute(query)
            return bool(res.unique().scalar_one_or_none())


class GameState(Base):
    __tablename__ = "game_states"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    games = relationship("Game", back_populates="state", lazy="joined")

    @classmethod
    async def has_fixtures(cls) -> bool:
        async with async_session() as session:
            query = select(GameState).limit(1)
            res = await session.execute(query)
            return bool(res.unique().scalar_one_or_none())

    @classmethod
    async def add_many(
        cls, instances: List["GameState"]
    ) -> List["GameState"]:
        async with async_session() as session:
            session.add_all(instances)
            await session.commit()
            return instances


class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, autoincrement=True)
    group_tg_id = Column(BigInteger, index=True, nullable=False)
    join_key = Column(String, index=True, unique=True)
    join_message_tg_id = Column(Integer, index=True)
    extend = Column(
        Integer, nullable=False, server_default=DefaultClause("0")
    )
    locale = Column(String(2), nullable=False, server_default="en")
    location_id = Column(
        Integer, ForeignKey("locations.id", ondelete="SET NULL")
    )
    is_allowed = Column(Boolean, nullable=False, default=False)
    state_id = Column(
        Integer,
        ForeignKey("game_states.id", ondelete="CASCADE"),
        nullable=False,
        default=1,
    )
    state = relationship("GameState", back_populates="games")
    location = relationship("Location", back_populates="games", lazy="joined")
    players = relationship("Player", back_populates="game", lazy="selectin")

    async def __aenter__(self):
        self.join_key = str(uuid.uuid4())
        self.state_id = 2
        self.location = await Location.get_random()
        self.extend = 0
        await self.save()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.join_key = None
        self.state_id = 1
        self.location_id = None
        self.join_message_tg_id = None
        self.extend = 0
        await self.save()
        await self.delete_players()

    @property
    def player_ids(self) -> List[int]:
        _player_ids = []
        for player in self.players:
            _player_ids.append(player.user.tg_id)
        return _player_ids

    async def all_players_voted(self) -> bool:
        players = await self.get_players()
        for player in players:
            if not player.votes:
                return False
        return True

    async def get_players(self) -> Iterable["Player"]:
        async with async_session() as session:
            query = select(Player).filter(Player.game_id == self.id)
            res = await session.execute(query)
            return res.scalars().unique().all()

    async def delete_players(self):
        async with async_session() as session:
            await session.execute(
                delete(Player).filter(
                    Player.id.in_(
                        select(Player.id).filter(Player.game_id == self.id)
                    )
                )
            )
            await session.commit()

    @classmethod
    async def get(
        cls, join_key: str = None, group_tg_id: int = None
    ) -> Optional["Game"]:
        if not join_key and not group_tg_id:
            raise ValueError("At least one argument must be specified")
        async with async_session() as session:
            query = select(Game)
            if join_key is not None:
                query = query.filter(Game.join_key == join_key)
            if group_tg_id is not None:
                query = query.filter(Game.group_tg_id == group_tg_id)
            res = await session.execute(query)
            return res.scalar()

    @classmethod
    async def get_count(cls) -> int:
        async with async_session() as session:
            query = select(func.count()).select_from(Game)
            res = await session.execute(query)
            return res.scalar()

    @classmethod
    async def get_active_count(cls) -> int:
        async with async_session() as session:
            query = (
                select(func.count())
                .select_from(Game)
                .filter(Game.state_id != 1)
            )
            res = await session.execute(query)
            return res.scalar()

    async def save(self):
        async with async_session() as session:
            session.add(self)
            await session.commit()

    async def refresh(self, attrs: Iterable[str] = None):
        async with async_session() as session:
            session.add(self)
            await session.refresh(self, attribute_names=attrs)

    class GameActiveError(Exception):
        pass


class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    game_id = Column(
        Integer,
        ForeignKey("games.id", ondelete="CASCADE"),
        nullable=False,
    )
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="SET NULL"))
    user = relationship("User", back_populates="players", lazy="joined")
    game = relationship("Game", back_populates="players", lazy="joined")
    role = relationship("Role", back_populates="players")
    votes = relationship(
        "Vote",
        foreign_keys="Vote.player_id",
        lazy="joined",
        back_populates="player",
    )
    spy_voted = relationship(
        "Vote",
        foreign_keys="Vote.spy_id",
        lazy="joined",
        back_populates="spy_player",
    )

    @classmethod
    async def join_to_game(
        cls, game_id: int, user_id: int
    ) -> Optional["Player"]:
        async with async_session() as session:
            query = select(Player).filter(and_(Player.user_id == user_id))
            res = await session.execute(query)
            player = res.unique().scalar_one_or_none()
            if player:
                raise ValueError("Already in game")
            player = Player(user_id=user_id, game_id=game_id)
            session.add(player)
            await session.commit()
            return player

    async def save(self):
        async with async_session() as session:
            session.add(self)
            await session.commit()
        return self

    async def refresh(self):
        async with async_session() as session:
            session.add(self)
            await session.refresh(self)

    @classmethod
    async def get(cls, user_tg_id: int = None, _id: int = None):
        if not user_tg_id and not _id:
            raise ValueError("At least one argument must be provided")
        async with async_session() as session:
            query = select(Player)
            if user_tg_id:
                subquery = select(User.id).filter(User.tg_id == user_tg_id)
                query = query.filter(Player.user_id.in_(subquery))
            if _id:
                query = query.filter(Player.id == _id)
            res = await session.execute(query)
            return res.unique().scalar_one_or_none()


class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"))
    player = relationship(
        "Player",
        back_populates="votes",
        foreign_keys="Vote.player_id",
        lazy="joined",
    )
    spy_id = Column(Integer, ForeignKey("players.id", ondelete="CASCADE"))
    spy_player = relationship(
        "Player",
        back_populates="spy_voted",
        foreign_keys="Vote.spy_id",
        lazy="joined",
    )

    async def save(self):
        async with async_session() as session:
            session.add(self)
            await session.commit()


class Feedback(Base):
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(String(4096), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", lazy="joined", back_populates="feedbacks")

    async def save(self):
        async with async_session() as session:
            session.add(self)
            await session.commit()

    @classmethod
    async def get_last(self, limit: int = 10):
        async with async_session() as session:
            query = select(Feedback).order_by(desc(Feedback.id)).limit(limit)
            res = await session.execute(query)
            return res.scalars().all()
