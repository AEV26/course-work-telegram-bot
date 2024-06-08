import aiohttp
import json
from dataclasses import asdict
from .models.rent_object import RentObject, UpdateRentObjectInput
from .models.record import Record, UpdateRecordInput
from .models.rent_object_info import RentObjectInfo


class ObjectAlreadyExistsExcpetion(Exception):
    ...


class RecordNotFoundException(Exception):
    ...


class ObjectNotFoundException(Exception):
    ...


class UnprocessableEntityException(Exception):
    ...


class ServerInternalErrorException(Exception):
    ...


class RentObjectService:
    USER_ID_QUERY_PARAM = "userId"
    OBJECT_NAME_QUERY_PARAM = "objectName"
    RECORD_INDEX_QUERY_PARAM = "recordIndex"

    def __init__(self, uri: str):
        self.uri = uri

    async def add_object(self, user_id: int, rent_object: RentObject):
        data = {"user_id": user_id, "object": rent_object.to_dict()}
        endpoint = "/addObject"
        text, status = await self._request("POST", endpoint, data=json.dumps(data))
        self._process_status(text, status)

    async def delete_object(self, user_id: int, object_name: str):
        data = {"user_id": user_id, "object_name": object_name}
        endpoint = "/deleteObject"
        text, status = await self._request("POST", endpoint, data=json.dumps(data))
        self._process_status(text, status)

    async def update_object(
        self, user_id: int, object_name: str, update: UpdateRentObjectInput
    ):
        data = {
            "user_id": user_id,
            "object_name": object_name,
            "update_input": asdict(update),
        }
        endpoint = "/updateObject"
        text, status = await self._request("POST", endpoint, data=json.dumps(data))
        self._process_status(text, status)

    async def get_by_name(self, user_id: int, object_name: str) -> RentObject:
        endpoint = "/getObject"
        params = {
            self.OBJECT_NAME_QUERY_PARAM: object_name,
            self.USER_ID_QUERY_PARAM: user_id,
        }
        text, status = await self._request("GET", endpoint, params=params)
        self._process_status(text, status)

        data = json.loads(text)

        return RentObject.from_dict(data)

    async def get_all(self, user_id: int) -> list[RentObject]:
        endpoint = "/getAll"
        params = {self.USER_ID_QUERY_PARAM: user_id}

        text, status = await self._request("GET", endpoint, params=params)
        self._process_status(text, status)

        data = json.loads(text)

        objects = []
        for el in data:
            objects.append(RentObject.from_dict(el))

        return objects

    async def add_record(self, user_id: int, object_name: str, record: Record):
        endpoint = "/addRecord"
        data = {
            "user_id": user_id,
            "object_name": object_name,
            "record": record.to_dict(),
        }

        text, status = await self._request("POST", endpoint, data=json.dumps(data))
        self._process_status(text, status)

    async def delete_record(self, user_id: int, object_name: str, record_index: int):
        endpoint = "/deleteRecord"
        data = {
            "user_id": user_id,
            "object_name": object_name,
            "record_index": record_index,
        }

        text, status = await self._request("POST", endpoint, data=json.dumps(data))
        self._process_status(text, status)

    async def update_record(
        self,
        user_id: int,
        object_name: str,
        record_index: int,
        update: UpdateRecordInput,
    ):
        endpoint = "/updateRecord"
        data = {
            "user_id": user_id,
            "object_name": object_name,
            "record_index": record_index,
            "update_input": update.to_dict(),
        }

        text, status = await self._request("POST", endpoint, data=json.dumps(data))
        self._process_status(text, status)

    async def get_reccord(
        self, user_id: int, object_name: str, record_index: int
    ) -> Record:
        endpoint = "/getRecord"
        params = {
            "user_id": user_id,
            "object_name": object_name,
            "record_index": record_index,
        }

        text, status = await self._request("GET", endpoint, params=params)
        self._process_status(text, status)

        data = json.loads(text)

        return Record.from_dict(data)

    async def get_all_records(self, user_id: int, object_name: str) -> list[Record]:
        endpoint = "/getRecords"
        params = {
            self.USER_ID_QUERY_PARAM: user_id,
            self.OBJECT_NAME_QUERY_PARAM: object_name,
        }

        text, status = await self._request("GET", endpoint, params=params)
        self._process_status(text, status)

        data = json.loads(text)
        records = []
        for el in data:
            records.append(Record.from_dict(el))

        return records

    async def get_object_info(self, user_id: int, object_name: str) -> RentObjectInfo:
        endpoint = "/getObjectInfo"
        params = {
            self.USER_ID_QUERY_PARAM: user_id,
            self.OBJECT_NAME_QUERY_PARAM: object_name,
        }

        text, status = await self._request("GET", endpoint, params=params)
        self._process_status(text, status)

        data = json.loads(text)

        return RentObjectInfo.from_dict(data)

    def _process_status(self, text: str, status: int):
        match status:
            case 404:
                if "Object" in text:
                    raise ObjectNotFoundException(text)
                elif "Record" in text:
                    raise RecordNotFoundException(text)
            case 409:
                raise ObjectAlreadyExistsExcpetion(text)
            case 422:
                raise UnprocessableEntityException(text)
            case 500:
                raise ServerInternalErrorException(text)

    async def _request(self, method: str, endpoint: str, **kwargs):
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method,
                self.uri + endpoint,
                **kwargs,
            ) as resp:
                return await resp.text(), resp.status
