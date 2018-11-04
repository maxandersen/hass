"""
Sensor for AfterShip.

Gives a sensor of all non-delivered packages recorded in AfterShip.

Requires an api key which can be aquired from
https://secure.aftership.com/#/settings/api.

Example configuration:

sensor:
   - platform: aftership
     api_key: AFTERSHIP_API_KEY
"""
from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    ATTR_ATTRIBUTION, CONF_API_KEY, CONF_NAME)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

REQUIREMENTS = ['aftership==0.2']

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = 'Information provided by AfterShip'

DEFAULT_NAME = 'aftership'

ICON = 'mdi:package-variant-closed'

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=30)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the PostNL sensor platform."""
    import aftership

    apikey = config.get(CONF_API_KEY)
    name = config.get(CONF_NAME)
    api = aftership.APIv4(apikey)

    add_entities([AfterShipSensor(api, name)], True)


class AfterShipSensor(Entity):
    """Representation of a AfterShip sensor."""

    def __init__(self, api, name):
        """Initialize the AfterShip sensor."""
        self._name = name
        self._attributes = None
        self._state = None
        self._api = api

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return 'packages'

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def icon(self):
        """Icon to use in the frontend."""
        return ICON

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Update device state."""
        import aftership

        try:
            trackingstop = self._api.trackings.get()
            status_counts = {}

            for tracking in trackingstop['trackings']:
                status = tracking['tag']
                name = tracking['tracking_number']
                if status != 'Delivered':
                    status_counts[name] = status

            self._attributes = {
                ATTR_ATTRIBUTION: ATTRIBUTION,
                **status_counts
            }

            self._state = len(status_counts)
        except aftership.APIv4RequestException as error:
            _LOGGER.exception(
                "Error when using the AfterShip webservice: %s %s %s",
                error.code(), error.type(), error.message()
            )
            return
