import aiohttp
import pytest
from aioresponses import aioresponses

from pykomfovent.client import KomfoventAuthError, KomfoventClient, KomfoventConnectionError

MAIN_XML = (
    b'<?xml version="1.0" encoding="windows-1250"?> <A><OMO>NORMALNY</OMO>'
    b"<AI0>20.9</AI0><AI1>23.2</AI1><AI2>5.4</AI2><SAF>50</SAF><EAF>50</EAF>"
    b"<FCG>47</FCG><EC1>87</EC1><EC2>305</EC2><EC3>64</EC3><EC4>0</EC4>"
    b"<EC5A>0.41</EC5A><EC5D>0.35</EC5D><EC6D>1.21</EC6D><EC6M>42.13</EC6M>"
    b"<EC6T>204.73</EC6T><EC7D>0</EC7D><EC7M>0</EC7M><EC7T>0.04</EC7T>"
    b"<EC8D>3.24</EC8D><EC8M>184.41</EC8M><EC8T>1285.67</EC8T><ST>21.0</ST>"
    b"<ET></ET><AQ>25</AQ><AH>25</AH><VF>203571212</VF></A>"
) + b" " * 200

DETAIL_XML = (
    b'<?xml version="1.0" encoding="windows-1250"?> '
    b"<V><SFI>50</SFI><EFI>50</EFI><HE>6</HE><EH>0</EH></V>"
) + b" " * 200

LOGIN_FAIL = b"""<p>Niepoprawne haslo!</p>"""

SCHEDULE_RESPONSE = b"var str={'p0r0':[1,2,3],'p0r1':[4,5,6]};" + b" " * 200


@pytest.fixture
def mock_aiohttp() -> aioresponses:
    with aioresponses() as m:
        yield m


async def test_authenticate_success(mock_aiohttp: aioresponses) -> None:
    mock_aiohttp.post("http://192.168.0.137:80/", body=b"x" * 200)

    client = KomfoventClient("192.168.0.137", "user", "user")
    result = await client.authenticate()
    await client.close()

    assert result is True


async def test_authenticate_failure(mock_aiohttp: aioresponses) -> None:
    mock_aiohttp.post("http://192.168.0.137:80/", body=LOGIN_FAIL)

    client = KomfoventClient("192.168.0.137", "user", "wrong")
    result = await client.authenticate()
    await client.close()

    assert result is False


async def test_get_state(mock_aiohttp: aioresponses) -> None:
    mock_aiohttp.post("http://192.168.0.137:80/i.asp", body=MAIN_XML)
    mock_aiohttp.post("http://192.168.0.137:80/det.asp", body=DETAIL_XML)

    client = KomfoventClient("192.168.0.137", "user", "user")
    state = await client.get_state()
    await client.close()

    assert state.mode == "NORMALNY"
    assert state.supply_temp == 20.9
    assert state.filter_contamination == 47.0


async def test_context_manager(mock_aiohttp: aioresponses) -> None:
    mock_aiohttp.post("http://192.168.0.137:80/i.asp", body=MAIN_XML)
    mock_aiohttp.post("http://192.168.0.137:80/det.asp", body=DETAIL_XML)

    async with KomfoventClient("192.168.0.137", "user", "user") as client:
        state = await client.get_state()
        assert state.mode == "NORMALNY"


async def test_auth_error_on_get_state(mock_aiohttp: aioresponses) -> None:
    mock_aiohttp.post("http://192.168.0.137:80/i.asp", body=LOGIN_FAIL)

    client = KomfoventClient("192.168.0.137", "user", "wrong")
    with pytest.raises(KomfoventAuthError):
        await client.get_state()
    await client.close()


async def test_connection_error(mock_aiohttp: aioresponses) -> None:
    for _ in range(3):
        mock_aiohttp.post("http://192.168.0.137:80/", exception=aiohttp.ClientError("timeout"))

    client = KomfoventClient("192.168.0.137", "user", "user")
    with pytest.raises(KomfoventConnectionError):
        await client.authenticate()
    await client.close()


async def test_close_without_session() -> None:
    client = KomfoventClient("192.168.0.137", "user", "user")
    await client.close()


async def test_set_mode(mock_aiohttp: aioresponses) -> None:
    mock_aiohttp.post("http://192.168.0.137:80/i.asp", body=b"x" * 200)

    client = KomfoventClient("192.168.0.137", "user", "user")
    await client.set_mode("intensive")
    await client.close()


async def test_set_mode_invalid(mock_aiohttp: aioresponses) -> None:
    client = KomfoventClient("192.168.0.137", "user", "user")
    with pytest.raises(ValueError, match="Unknown mode"):
        await client.set_mode("invalid")
    await client.close()


async def test_set_supply_temp(mock_aiohttp: aioresponses) -> None:
    mock_aiohttp.post("http://192.168.0.137:80/i.asp", body=b"x" * 200)

    client = KomfoventClient("192.168.0.137", "user", "user")
    await client.set_supply_temp(22.5)
    await client.close()


async def test_set_supply_temp_out_of_range() -> None:
    client = KomfoventClient("192.168.0.137", "user", "user")
    with pytest.raises(ValueError, match="out of valid range"):
        await client.set_supply_temp(5.0)
    with pytest.raises(ValueError, match="out of valid range"):
        await client.set_supply_temp(40.0)
    await client.close()


async def test_set_register(mock_aiohttp: aioresponses) -> None:
    mock_aiohttp.post("http://192.168.0.137:80/", body=b"x" * 200)

    client = KomfoventClient("192.168.0.137", "user", "user")
    await client.set_register(100, "50")
    await client.close()


async def test_get_schedule(mock_aiohttp: aioresponses) -> None:
    mock_aiohttp.post("http://192.168.0.137:80/sh.cfg", body=SCHEDULE_RESPONSE)

    client = KomfoventClient("192.168.0.137", "user", "user")
    schedule = await client.get_schedule()
    await client.close()

    assert "p0r0" in schedule
    assert schedule["p0r0"] == [1, 2, 3]


async def test_get_schedule_parse_error(mock_aiohttp: aioresponses) -> None:
    mock_aiohttp.post("http://192.168.0.137:80/sh.cfg", body=b"invalid" + b" " * 200)

    client = KomfoventClient("192.168.0.137", "user", "user")
    with pytest.raises(KomfoventConnectionError, match="Failed to parse schedule"):
        await client.get_schedule()
    await client.close()


async def test_set_schedule(mock_aiohttp: aioresponses) -> None:
    mock_aiohttp.post("http://192.168.0.137:80/", body=b"x" * 200)

    client = KomfoventClient("192.168.0.137", "user", "user")
    await client.set_schedule({"100": 1, "101": 2})
    await client.close()


async def test_retry_on_connection_error(mock_aiohttp: aioresponses) -> None:
    mock_aiohttp.post("http://192.168.0.137:80/", exception=aiohttp.ClientError("fail"))
    mock_aiohttp.post("http://192.168.0.137:80/", exception=aiohttp.ClientError("fail"))
    mock_aiohttp.post("http://192.168.0.137:80/", body=b"x" * 200)

    client = KomfoventClient("192.168.0.137", "user", "user")
    result = await client.authenticate()
    await client.close()

    assert result is True
