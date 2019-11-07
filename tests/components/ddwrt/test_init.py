"""Test DD-WRT platform setup."""
from homeassistant.setup import async_setup_component

from homeassistant.components.ddwrt import (
    DOMAIN,
    DATA_DDWRT,
)
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, CONF_HOST

from tests.common import MockDependency, mock_coro


async def test_conf_password_or_pub_key_required(hass):
    """Test creating an DD-WRT scanner without a pass or pubkey."""
    config = {
        DOMAIN: {
            'fake_dev': {
                CONF_HOST: "fake_host",
                CONF_USERNAME: "fake_user"
            }
        }
    }
    with MockDependency("aioddwrt.ddwrt") as mocked_ddwrt:
        mocked_ddwrt.DdWrt().is_connected = False
        assert not await async_setup_component(hass, DOMAIN, config)


async def test_conf_password_no_pubkey(hass):
    """Test creating an AsusWRT scanner with a password and no pubkey."""
    config = {
        DOMAIN: {
            'fake_dev': {
                CONF_HOST: "fake_host",
                CONF_USERNAME: "fake_user",
                CONF_PASSWORD: "4321",
            }
        }
    }
    with MockDependency("aioddwrt.ddwrt") as mocked_ddwrt:
        mocked_ddwrt.DdWrt().async_get_wl = mock_coro(return_value={})
        assert await async_setup_component(hass, DOMAIN, config)
        assert hass.data[DATA_DDWRT] is not None
