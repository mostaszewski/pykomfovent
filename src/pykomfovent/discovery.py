import asyncio
import socket
from dataclasses import dataclass

import aiohttp


@dataclass(frozen=True, slots=True)
class DiscoveredDevice:
    host: str
    name: str


def get_local_subnet() -> str | None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            return ".".join(ip.split(".")[:3]) + ".0/24"
    except OSError:
        return None


class KomfoventDiscovery:
    def __init__(
        self, subnet: str | None = None, timeout: float = 2.0, max_concurrent: int = 10
    ) -> None:
        self._subnet = subnet or get_local_subnet()
        self._timeout = timeout
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def _check_host(
        self, session: aiohttp.ClientSession, host: str
    ) -> DiscoveredDevice | None:
        async with self._semaphore:
            try:
                async with session.get(
                    f"http://{host}/",
                    timeout=aiohttp.ClientTimeout(total=self._timeout),
                ) as resp:
                    server = resp.headers.get("Server", "")
                    if server.startswith("C6"):
                        content_bytes = await resp.read()
                        content = content_bytes.decode("windows-1250", errors="ignore")
                        name = "Komfovent"
                        try:
                            start = content.index("<title>") + 7
                            end = content.index("</title>", start)
                            name = content[start:end].strip() or "Komfovent"
                        except ValueError:
                            pass
                        return DiscoveredDevice(host=host, name=name)
            except (aiohttp.ClientError, TimeoutError, OSError):
                pass
            return None

    async def discover(self) -> list[DiscoveredDevice]:
        if not self._subnet:
            return []

        base = ".".join(self._subnet.split(".")[:3])
        hosts = [f"{base}.{i}" for i in range(1, 255)]

        async with aiohttp.ClientSession() as session:
            tasks = [self._check_host(session, host) for host in hosts]
            results = await asyncio.gather(*tasks)

        return [r for r in results if r is not None]
