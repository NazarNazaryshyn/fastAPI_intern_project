from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from httpx import AsyncClient
import pytest_asyncio
from src.base import Base
from ..main import app, startup
import pytest
from src.config import settings


SQLALCHEMY_DATABASE_URL = settings.TEST_DATABASE_URL

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL
# )
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestSession = sessionmaker(expire_on_commit=False, class_=AsyncSession, bind=async_engine)

# Base.metadata.create_all(bind=engine)

# @pytest_asyncio.fixture(scope="session")
# async def test_db_setup_sessionmaker():
#     # assert if we use TEST_DB URL for 100%
#     assert config.settings.ENVIRONMENT == "PYTEST"
#     assert str(async_engine.url) == config.settings.TEST_SQLALCHEMY_DATABASE_URI
#
#     # always drop and create test db tables between tests session
#     async with async_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)
#
#
# @pytest_asyncio.fixture(autouse=True)
# async def session(test_db_setup_sessionmaker) -> AsyncGenerator[AsyncSession, None]:
#     async with async_session() as session:
#         yield session
#
#         # delete all data from all tables after test
#         for name, table in Base.metadata.tables.items():
#             await session.execute(delete(table))
#         await session.commit()
#
#
# @pytest_asyncio.fixture(scope="session")
# async def client() -> AsyncGenerator[AsyncClient, None]:
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         client.headers.update({"Host": "localhost"})
#         yield client

# def override_get_db():
#     try:
#         db = TestingSessionLocal()
#         yield db
#     finally:
#         db.close()
#
#
# app.dependency_overrides[startup] = override_get_db

@pytest.fixture()
async def get_test_db():
    Base.metadata.drop_all(bind=async_engine)
    Base.metadata.create_all(bind=async_engine)
    async with TestSession() as db:
        yield db
#
#
# @pytest.fixture()
# async def client_func(get_test_db):
#     async def test_db():
#         try:
#             yield get_test_db
#         finally:
#             await get_test_db.close()
#     app.dependency_overrides[startup] = test_db
# def override_get_db():
#     try:
#         db = TestSession()
#         yield db
#     finally:
#         db.close()
#
# @pytest.fixture()
# async def reload_db():
#     async with async_engine.begin() as conn:
#         app.dependency_overrides[startup] = override_get_db
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)


client = TestClient(app)


data = {
    "name": "Ivan",
    "surname": "Ivanov",
    "age": 22,
    "email": "ivan@gmail.com",
    "password": "ivan12345"
}
headers = {'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlBCc193ZHMzVkxtZVpnLUt1SEhkTCJ9.eyJodHRwczovL2V4YW1wbGUuY29tL2VtYWlsIjoibi5uYXphcnlzaHluQGdtYWlsLmNvbSIsImlzcyI6Imh0dHBzOi8vZGV2LWt6azlqcjN4LnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJnb29nbGUtb2F1dGgyfDEwMDIxMjAwMjk4MjY3ODE1MDQzMiIsImF1ZCI6WyJodHRwczovL2F1dGgtYXBpLWludGVybi8iLCJodHRwczovL2Rldi1rems5anIzeC51cy5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNjY4MDcwNDE3LCJleHAiOjE2NjgxNTY4MTcsImF6cCI6IkJMUkNLcElwNUR4WHU3aWt3V0NBTUVoWjVBWFhteTFhIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCJ9.ebINJhmKCbSie5ZkwICqdsNhHFGWcKf99TizMFMXhis433Vl-DmTe5140tiBJtJ3iIIFu5IdJRevi_-_eP3D70nS40WQDQWfUNPOnXgIjU5V5WRqbdxMV-bzh4IDUSiCQf9mpdckgAL0WQbnfypb1j6BS7_LWxPF31CulKhX8hi28-NyTfK6Ga6e_UiXN4DbRdKXkjhunYrMTFwsSyNL_WP8Bj4IIoDzWiQJ8Vhi5Jpl7lct-q-2UCGAxO-NwCDrVmhecIMQ6vkVeq2X84wpb92PYb5kwK9lwN_k5bu6pro8VPPbGQv7JXA7gPaNlKtbhZCk5U01tdqvh8RtcmBSYQ'}


@pytest.mark.anyio
async def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "Working"}


@pytest.mark.anyio
async def test_create_user(get_test_db):
    response = client.post("/user/", json=data)
    print(response.json())
    assert response.status_code == 201
    assert response.json() == {"id": 1,
                               "name": "Ivan",
                               "surname": "Ivanov",
                               "age": 22,
                               "email": "ivan@gmail.com"}


# @pytest.mark.anyio
# def test_get_users():
#     get_token = client.post("/auth/login", json={"email": "ivan@gmail.com",
#                                                  "password": "ivan12345"})
#
#     token = get_token.json()
#     print(f"!!!!!!!!!!!!!!!!!!!!!!!!!{token}!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
#     response = client.get("/user/", headers={"Authorization": f"Bearer {token}"})
#
#     assert response.status_code == 200
#     assert response.json() ==  {"id": 1,
#                                "name": "Ivan",
#                                "surname": "Ivanov",
#                                "age": 22,
#                                "email": "ivan@gmail.com"}





# @pytest.mark.anyio
# def test_create_user_d():
#     response = client.post("/user/", json=data)
#     assert response.status_code == 201
#     assert response.json() == {"id": 1,
#                                "name": "Ivan",
#                                "surname": "Ivanov",
#                                "age": 22,
#                                "email": "ivan@gmail.com"}

