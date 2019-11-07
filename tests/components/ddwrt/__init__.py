"""Tests for the asuswrt component."""

from homeassistant.components.ddwrt import (
    CONF_PROTOCOL,
    CONF_MODE,
    DOMAIN,
    CONF_PORT,
    DATA_DDWRT,
)
from homeassistant.const import CONF_PLATFORM, CONF_PASSWORD, CONF_USERNAME, \
    CONF_HOST

VALID_PLATFORM_CONFIG_ROUTER_SSH = {
    DOMAIN: {
        CONF_HOST: "fake_host",
        CONF_USERNAME: "fake_user",
        CONF_PROTOCOL: "ssh",
        CONF_MODE: "router",
        CONF_PORT: "22",
    }
}

VALID_PLATFORM_CONFIG_ROUTER_HTTP = {}

INVALID_PLATFORM_CONFIG_ROUTER = {}

