from __future__ import annotations

import urllib.parse
import uuid
from typing import Any, Dict, Optional

from .._types import ApiKey, ApiKeyListResult, CreateApiKeyResponse
from ._base import AsyncBaseResource, BaseResource

# Sentinel: distinguishes "not provided" from "explicitly None" so callers can
# clear nullable fields (agent_label, line_id, monthly_cap_cents) on PATCH.
_UNSET: Any = object()


class KeysResource(BaseResource):
    """Manage child api keys minted by the calling service key."""

    def create(
        self,
        *,
        name: str,
        agent_label: Optional[str] = None,
        line_id: Optional[str] = None,
        permissions: str = "full",
        monthly_cap_cents: Optional[int] = None,
        environment: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> CreateApiKeyResponse:
        idem = idempotency_key or str(uuid.uuid4())
        body: Dict[str, Any] = {"name": name, "permissions": permissions}
        if agent_label is not None:
            body["agent_label"] = agent_label
        if line_id is not None:
            body["line_id"] = line_id
        if monthly_cap_cents is not None:
            body["monthly_cap_cents"] = monthly_cap_cents
        if environment is not None:
            body["environment"] = environment
        data = self._client.request(
            "POST", "/keys", body=body, headers={"Idempotency-Key": idem}
        )
        return CreateApiKeyResponse.from_dict(data.get("key", {}))

    def list(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> ApiKeyListResult:
        data = self._client.request(
            "GET", "/keys", query={"limit": limit, "offset": offset}
        )
        return ApiKeyListResult.from_dict(data)

    def get(self, key_id: str) -> ApiKey:
        encoded = urllib.parse.quote(key_id, safe="")
        data = self._client.request("GET", f"/keys/{encoded}")
        return ApiKey.from_dict(data.get("key", {}))

    def update(
        self,
        key_id: str,
        *,
        name: Optional[str] = None,
        agent_label: Any = _UNSET,
        line_id: Any = _UNSET,
        permissions: Optional[str] = None,
        monthly_cap_cents: Any = _UNSET,
    ) -> ApiKey:
        encoded = urllib.parse.quote(key_id, safe="")
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if agent_label is not _UNSET:
            body["agent_label"] = agent_label
        if line_id is not _UNSET:
            body["line_id"] = line_id
        if permissions is not None:
            body["permissions"] = permissions
        if monthly_cap_cents is not _UNSET:
            body["monthly_cap_cents"] = monthly_cap_cents
        data = self._client.request("PATCH", f"/keys/{encoded}", body=body)
        return ApiKey.from_dict(data.get("key", {}))

    def delete(self, key_id: str) -> ApiKey:
        encoded = urllib.parse.quote(key_id, safe="")
        data = self._client.request("DELETE", f"/keys/{encoded}")
        return ApiKey.from_dict(data.get("key", {}))

    def rotate(
        self,
        key_id: str,
        *,
        idempotency_key: Optional[str] = None,
    ) -> CreateApiKeyResponse:
        encoded = urllib.parse.quote(key_id, safe="")
        idem = idempotency_key or str(uuid.uuid4())
        data = self._client.request(
            "POST",
            f"/keys/{encoded}/rotate",
            headers={"Idempotency-Key": idem},
        )
        return CreateApiKeyResponse.from_dict(data.get("key", {}))


class AsyncKeysResource(AsyncBaseResource):
    """Async variant — identical interface, awaitable methods."""

    async def create(
        self,
        *,
        name: str,
        agent_label: Optional[str] = None,
        line_id: Optional[str] = None,
        permissions: str = "full",
        monthly_cap_cents: Optional[int] = None,
        environment: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> CreateApiKeyResponse:
        idem = idempotency_key or str(uuid.uuid4())
        body: Dict[str, Any] = {"name": name, "permissions": permissions}
        if agent_label is not None:
            body["agent_label"] = agent_label
        if line_id is not None:
            body["line_id"] = line_id
        if monthly_cap_cents is not None:
            body["monthly_cap_cents"] = monthly_cap_cents
        if environment is not None:
            body["environment"] = environment
        data = await self._client.request(
            "POST", "/keys", body=body, headers={"Idempotency-Key": idem}
        )
        return CreateApiKeyResponse.from_dict(data.get("key", {}))

    async def list(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> ApiKeyListResult:
        data = await self._client.request(
            "GET", "/keys", query={"limit": limit, "offset": offset}
        )
        return ApiKeyListResult.from_dict(data)

    async def get(self, key_id: str) -> ApiKey:
        encoded = urllib.parse.quote(key_id, safe="")
        data = await self._client.request("GET", f"/keys/{encoded}")
        return ApiKey.from_dict(data.get("key", {}))

    async def update(
        self,
        key_id: str,
        *,
        name: Optional[str] = None,
        agent_label: Any = _UNSET,
        line_id: Any = _UNSET,
        permissions: Optional[str] = None,
        monthly_cap_cents: Any = _UNSET,
    ) -> ApiKey:
        encoded = urllib.parse.quote(key_id, safe="")
        body: Dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if agent_label is not _UNSET:
            body["agent_label"] = agent_label
        if line_id is not _UNSET:
            body["line_id"] = line_id
        if permissions is not None:
            body["permissions"] = permissions
        if monthly_cap_cents is not _UNSET:
            body["monthly_cap_cents"] = monthly_cap_cents
        data = await self._client.request("PATCH", f"/keys/{encoded}", body=body)
        return ApiKey.from_dict(data.get("key", {}))

    async def delete(self, key_id: str) -> ApiKey:
        encoded = urllib.parse.quote(key_id, safe="")
        data = await self._client.request("DELETE", f"/keys/{encoded}")
        return ApiKey.from_dict(data.get("key", {}))

    async def rotate(
        self,
        key_id: str,
        *,
        idempotency_key: Optional[str] = None,
    ) -> CreateApiKeyResponse:
        encoded = urllib.parse.quote(key_id, safe="")
        idem = idempotency_key or str(uuid.uuid4())
        data = await self._client.request(
            "POST",
            f"/keys/{encoded}/rotate",
            headers={"Idempotency-Key": idem},
        )
        return CreateApiKeyResponse.from_dict(data.get("key", {}))
