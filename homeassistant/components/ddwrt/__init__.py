"""The ddwrt component."""
import logging

import voluptuous as vol

from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_PORT,
    CONF_MODE,
    CONF_PROTOCOL,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.exceptions import PlatformNotReady

_LOGGER = logging.getLogger(__name__)

CONF_SENSORS = "sensors"
CONF_SSH_KEY = "ssh_key"

DOMAIN = "ddwrt"
DATA_DDWRT = DOMAIN
DEFAULT_SSH_PORT = 22

SECRET_GROUP = "Password or SSH Key"
SENSOR_TYPES = ["upload_speed", "download_speed", "download", "upload"]

DDWRT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Optional(CONF_PROTOCOL, default="http"):
            vol.In(["ssh", "telnet", "http"]),
        vol.Optional(CONF_MODE, default="router"): vol.In(["router", "ap"]),
        vol.Optional(CONF_PORT, default=DEFAULT_SSH_PORT): cv.port,
        vol.Exclusive(CONF_PASSWORD, SECRET_GROUP): cv.string,
        vol.Exclusive(CONF_SSH_KEY, SECRET_GROUP): cv.isfile,
        vol.Optional(CONF_SENSORS): vol.All(
            cv.ensure_list, [vol.In(SENSOR_TYPES)]
        ),
    }
)
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: {cv.string: DDWRT_SCHEMA},
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Set up the asuswrt component."""
    from aioddwrt.ddwrt import DdWrt

    conf = config[DOMAIN]

    ddwrt = {}
    for ddwrt_dev in conf:
        if ddwrt_dev['protocol'] == 'http':
            session = await async_get_clientsession(hass, verify_ssl=False)
        else:
            session = None
        device = DdWrt(http_session=session, **ddwrt_dev)
        try:
            await device.async_get_wl()
        except ConnectionError as e:
            _LOGGER.debug(f"Failed to setup ddwrt platform: {e}")
            raise PlatformNotReady
        ddwrt[ddwrt_dev] = device

    hass.data[DATA_DDWRT] = {'api': ddwrt, 'cache': {}}

    return True
