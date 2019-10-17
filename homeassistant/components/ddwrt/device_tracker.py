"""Support for DD-WRT routers."""
import logging
import voluptuous as vol

from homeassistant.const import CONF_NAME
from homeassistant.helpers import config_validation as cv
from homeassistant.components.device_tracker import (
    DOMAIN,
    PLATFORM_SCHEMA,
    DeviceScanner
)

from . import DATA_DDWRT

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
})

_LOGGER = logging.getLogger(__name__)


async def async_get_scanner(hass, config):
    """Validate the configuration and return an DD-WRT scanner."""
    name = config[DOMAIN][CONF_NAME]
    data = hass.data[DATA_DDWRT]
    if name not in data['api']:
        _LOGGER.warning(f"Did not find '{name}' in configured ddwrt"
                        f"platform devices: {','.join(data['api'].keys())}")
        return None
    scanner = DdWrtDeviceScanner(data[name], data['cache'])
    try:
        await scanner.async_connect()
    except ConnectionError:
        return None
    return scanner


class DdWrtDeviceScanner(DeviceScanner):
    """This class queries a router running DDWRT firmware."""

    # Eighth attribute needed for mode (AP mode vs router mode)
    def __init__(self, api, cache):
        """Initialize the scanner."""
        self.cache = cache
        self.api = api
        self.status = None

    async def async_connect(self):
        """Initialize connection to the router."""
        # Test connection to all routers and aps.
        _ = await self.api.async_get_wl()
        self.status = 'ONLINE'

    async def async_scan_devices(self):
        """Scan for new devices and return a list with found device IDs."""
        _LOGGER.debug(f"Scanning devices on {self.api.host}")
        try:
            detected = await self.api.async_get_wl()
        except ConnectionError:
            if self.status == 'ONLINE':
                _LOGGER.warning(f"Lost connection with ddwrt {self.api.host}")
            self.status = 'OFFLINE'
            return []
        # check if status needs to be updated
        if self.status == 'OFFLINE':
            _LOGGER.warning(f"Connection re-established with ddwrt "
                            f"{self.api.host}")
            self.status = 'ONLINE'
        return detected

    async def async_get_device_name(self, device):
        """Return the name of the given device or None if we don't know."""
        if device not in self.cache:
            # try to update the info if not found
            await self.async_update_cache()
            if device not in self.cache:
                return None

        return self.cache[device]['host']

    async def async_get_extra_attributes(self, device):
        """Get the extra attributes of a device."""
        if device not in self.cache:
            # try to update the info if not found
            await self.async_update_cache()
            if device not in self.cache:
                return None

        return self.cache[device]

    async def async_update_cache(self):
        """Update the extra information cache."""
        if self.api.mode == 'router' and self.status == 'ONLINE':
            self.cache.update(await self.api.async_get_leases())
