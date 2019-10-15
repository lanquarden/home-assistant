"""Support for DD-WRT routers."""
import logging

from homeassistant.components.device_tracker import DeviceScanner

from . import DATA_DDWRT

_LOGGER = logging.getLogger(__name__)


async def async_get_scanner(hass, config):
    """Validate the configuration and return an DD-WRT scanner."""
    scanner = DdWrtDeviceScanner(hass.data[DATA_DDWRT])
    await scanner.async_connect()
    return scanner if scanner.success_init else None


class DdWrtDeviceScanner(DeviceScanner):
    """This class queries a router running DDWRT firmware."""

    # Eighth attribute needed for mode (AP mode vs router mode)
    def __init__(self, equipment):
        """Initialize the scanner."""
        self.cache = {}
        self.success_init = False
        self.equipment = equipment

    async def async_connect(self):
        """Initialize connection to the router."""
        # Test connection to all routers and aps.
        self.success_init = True
        for device in self.equipment:
            _ = await device.async_get_wl()
            if not device.is_connected:
                self.success_init = False

    async def async_scan_devices(self):
        """Scan for new devices and return a list with found device IDs."""
        detected = []
        _LOGGER.debug("Scanning devices on DDWRT")
        for device in self.equipment:
            detected.extend(await device.async_get_wl())

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
        """Updating the extra information cache."""
        self.cache = {}
        for device in self.equipment:
            if device.mode == 'router':
                self.cache.update(await device.async_get_leases())
