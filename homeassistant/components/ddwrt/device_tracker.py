"""Support for DD-WRT routers."""
import logging

from homeassistant.components.device_tracker import DeviceScanner

from . import DATA_DDWRT

_LOGGER = logging.getLogger(__name__)


async def async_get_scanner(hass, config):
    """Validate the configuration and return an DD-WRT scanner."""
    scanner = DdWrtDeviceScanner(hass.data[DATA_DDWRT])
    try:
        await scanner.async_connect()
    except ConnectionError:
        return None
    return scanner


class DdWrtDeviceScanner(DeviceScanner):
    """This class queries a router running DDWRT firmware."""

    # Eighth attribute needed for mode (AP mode vs router mode)
    def __init__(self, equipment):
        """Initialize the scanner."""
        self.cache = {}
        self.equipment = equipment
        self.status = {}

    async def async_connect(self):
        """Initialize connection to the router."""
        # Test connection to all routers and aps.
        for device in self.equipment:
            _ = await device.async_get_wl()
            self.status[device.host] = 'ONLINE'

    async def async_scan_devices(self):
        """Scan for new devices and return a list with found device IDs."""
        detected = []
        _LOGGER.debug("Scanning devices on DDWRT")
        for device in self.equipment:
            try:
                detected.extend(await device.async_get_wl())
            except ConnectionError:
                if self.status[device.host] == 'ONLINE':
                    _LOGGER.warning(f"Lost connection with ddwrt "
                                    f"{device.host}")
                self.status[device.host] = 'OFFLINE'
                continue
            # check if status needs to be updated
            if self.status[device.host] == 'OFFLINE':
                _LOGGER.warning(f"Connection re-established with ddwrt "
                                f"{device.host}")
                self.status[device.host] = 'ONLINE'
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
        self.cache = {}
        for device in self.equipment:
            if device.mode == 'router' and \
                    self.status[device.host] == 'ONLINE':
                self.cache.update(await device.async_get_leases())
