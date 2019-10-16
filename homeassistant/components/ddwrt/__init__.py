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
from homeassistant.helpers.discovery import async_load_platform

_LOGGER = logging.getLogger(__name__)

CONF_REQUIRE_IP = "require_ip"
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
        DOMAIN: vol.Any(DDWRT_SCHEMA, [DDWRT_SCHEMA]),
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Set up the asuswrt component."""
    from aioddwrt.ddwrt import DdWrt

    conf = config[DOMAIN]
    if not isinstance(conf, list):
        conf = [conf]

    equipment = []
    for dev_conf in conf:
        device = DdWrt(**dev_conf)
        await device.async_get_wl()
        if not device.is_connected:
            _LOGGER.error("Unable to setup ddwrt component")
            return False
        equipment.append(device)

    hass.data[DATA_DDWRT] = equipment

    # hass.async_create_task(
    #     async_load_platform(
    #         hass, "sensor", DOMAIN, config[DOMAIN].get(CONF_SENSORS), config
    #     )
    # )

    hass.async_create_task(
        async_load_platform(hass, "device_tracker", DOMAIN, {}, config)
    )

    return True
