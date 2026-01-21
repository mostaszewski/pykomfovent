import asyncio
import json
import re
from types import TracebackType

import aiohttp

from pykomfovent.models import KomfoventState
from pykomfovent.parser import KomfoventParseError, parse_state

MODE_CODES = {"away": 1, "normal": 2, "intensive": 3, "boost": 4}
MAX_RETRIES = 3
RETRY_DELAY = 1


class KomfoventAuthError(Exception):
    pass


class KomfoventConnectionError(Exception):
    pass


class KomfoventClient:
    def __init__(self, host: str, username: str, password: str, port: int = 80) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._session: aiohttp.ClientSession | None = None

    @property
    def base_url(self) -> str:
        return f"http://{self._host}:{self._port}"

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=10, connect=5)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def __aenter__(self) -> "KomfoventClient":
        await self._ensure_session()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def _request(self, path: str, extra_data: dict[str, str] | None = None) -> bytes:
        session = await self._ensure_session()
        data: dict[str, str] = {"1": self._username, "2": self._password}
        if extra_data:
            data.update(extra_data)

        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                async with session.post(f"{self.base_url}{path}", data=data) as resp:
                    content = await resp.read()
                    if b"Niepoprawne" in content or len(content) < 100:
                        raise KomfoventAuthError("Invalid credentials")
                    return content
            except KomfoventAuthError:
                raise
            except aiohttp.ClientError as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY * (attempt + 1))

        raise KomfoventConnectionError(
            f"Connection failed after {MAX_RETRIES} attempts: {last_error}"
        )

    async def authenticate(self) -> bool:
        try:
            await self._request("/")
            return True
        except KomfoventAuthError:
            return False

    async def get_state(self) -> KomfoventState:
        main_xml = await self._request("/i.asp")
        detail_xml = await self._request("/det.asp")
        try:
            return parse_state(main_xml, detail_xml)
        except KomfoventParseError as e:
            raise KomfoventConnectionError(f"Failed to parse response: {e}") from e

    async def set_mode(self, mode: str) -> None:
        code = MODE_CODES.get(mode.lower())
        if code is None:
            raise ValueError(f"Unknown mode: {mode}. Valid: {list(MODE_CODES.keys())}")
        await self._request("/i.asp", {"3": str(code)})

    async def set_supply_temp(self, temp: float) -> None:
        if not 10.0 <= temp <= 35.0:
            raise ValueError(f"Temperature {temp} out of valid range (10-35°C)")
        await self._request("/i.asp", {"4": str(int(temp * 10))})

    async def set_register(self, register: int, value: str) -> None:
        await self._request("/", {str(register): value})

    async def get_schedule(self) -> dict[str, list[int]]:
        response = await self._request("/sh.cfg")
        text = response.decode("windows-1250", errors="ignore")
        match = re.search(r"var str=(\{.*\});", text)
        if not match:
            raise KomfoventConnectionError("Failed to parse schedule config")
        js = match.group(1)
        js = re.sub(r"'([^']+)'", r'"\1"', js)
        return json.loads(js)

    async def set_schedule(self, commands: dict[str, int]) -> None:
        str_commands = {k: str(v) for k, v in commands.items()}
        await self._request("/", str_commands)

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
