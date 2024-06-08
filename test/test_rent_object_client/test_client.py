import pytest
from app.service.rent_object_service import RentObjectService, ObjectNotFoundException
from app.service.models.rent_object import RentObject, UpdateRentObjectInput
from app.service.models.record import Record
from datetime import datetime


@pytest.fixture
def client():
    return RentObjectService(uri="http://localhost:8080")


@pytest.fixture
def dummyRecord():
    return Record(
        date=datetime.now(),
        rent=0,
        heat=0,
        exploitation=0,
        mop=0,
        renovation=0,
        tbo=0,
        electricity=0,
        earth_rent=0,
        other=0,
        security=0,
    )


TEST_USER_ID = 23


@pytest.mark.asyncio
async def test_client_add_object(client, dummyRecord: Record):
    obj = RentObject(name="object", description="test", area=100, records=[dummyRecord])
    await client.add_object(user_id=TEST_USER_ID, rent_object=obj)

    await client.delete_object(
        user_id=TEST_USER_ID,
        object_name=obj.name,
    )


@pytest.mark.asyncio
async def test_client_get_object(client):
    obj = RentObject(name="object", description="test", area=100, records=[])
    await client.add_object(user_id=TEST_USER_ID, rent_object=obj)

    got = await client.get_by_name(user_id=TEST_USER_ID, object_name=obj.name)

    assert got == obj

    await client.delete_object(
        user_id=TEST_USER_ID,
        object_name=obj.name,
    )


@pytest.mark.asyncio
async def test_client_update_object(client, dummyRecord: Record):
    obj = RentObject(name="object", description="test", area=100, records=[])
    await client.add_object(user_id=TEST_USER_ID, rent_object=obj)

    update = UpdateRentObjectInput(name="object_test")

    await client.update_object(
        user_id=TEST_USER_ID, object_name=obj.name, update=update
    )

    expected = RentObject(
        name=update.name,
        description=obj.description,
        area=obj.area,
        records=obj.records,
    )

    got = await client.get_by_name(user_id=TEST_USER_ID, object_name=update.name)
    assert expected == got

    with pytest.raises(ObjectNotFoundException):
        await client.delete_object(
            user_id=TEST_USER_ID,
            object_name=obj.name,
        )

    await client.delete_object(
        user_id=TEST_USER_ID,
        object_name=update.name,
    )


@pytest.mark.asyncio
async def test_client_get_all(client):
    objects = []
    for i in range(1, 11):
        obj = RentObject(name=f"object{i}", description="test", area=100, records=[])
        objects.append(obj)
        await client.add_object(user_id=TEST_USER_ID, rent_object=obj)

    got = await client.get_all(TEST_USER_ID)

    assert got == objects

    for obj in objects:
        await client.delete_object(TEST_USER_ID, obj.name)
