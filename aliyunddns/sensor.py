#!/usr/bin/env python
# encoding: utf-8
import logging

from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
from homeassistant.helpers.config_validation import (  # noqa
                                                     PLATFORM_SCHEMA)
from homeassistant.const import (CONF_NAME)

from homeassistant.helpers import config_validation as cv
import voluptuous as vol

import datetime
from datetime import timedelta

from homeassistant.helpers import event as evt
from homeassistant.core import callback

from . import aliddns

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = datetime.timedelta(hours=1)

DEFAULT_NAME = 'aliyun_ddns'

#多个sensors
CONF_ACCESSKEYID = "accessKeyId"
CONF_ACCESSSECRET = "accessSecret"
CONF_DOMAIN = "domain"
CONF_SUB_DOMAIN = "sub_domain"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_ACCESSKEYID,default=''): cv.string,
    vol.Optional(CONF_ACCESSSECRET,default=''): cv.string,
    vol.Optional(CONF_DOMAIN,default=''): cv.string,
    vol.Optional(CONF_SUB_DOMAIN,default=''): cv.string,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the sensor."""
    name = config.get(CONF_NAME)
    accessKeyId = config.get(CONF_ACCESSKEYID)
    accessSecret = config.get(CONF_ACCESSSECRET)
    domain = config.get(CONF_DOMAIN)
    sub_domain = config.get(CONF_SUB_DOMAIN)

    sensors = []

    sensors.append(AliyunDDNSSensor(
        hass, accessKeyId,accessSecret, domain,sub_domain, name))

    add_devices(sensors)


class AliyunDDNSSensor(Entity):
    """Implementation of a AirCat sensor."""

    def __init__(self, hass, accessKeyId,accessSecret, domain,sub_domain, name):
        """Initialize the AirCat sensor."""
        self._hass = hass
        self._name = name
        self._domain = domain
        self._sub_domain = sub_domain
        self._state = ""
        self._attributes = {}
        self._aliddns = aliddns.AliDDNS(accessKeyId,accessSecret,domain,sub_domain)
        # self.update()
        # @callback
        # def _listener_callback(_):
        #     self._update()
            
        # fire_date = datetime.datetime.utcnow() + timedelta(hours=8) + timedelta(seconds=30)
        # _LOGGER.info('notify_date')
        # _LOGGER.info(fire_date)
        # evt.async_track_point_in_time(
        #     self._hass, _listener_callback, fire_date
        # )


    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def state(self):
        """Return the state of the binary sensor."""
        return self._state 

    # @property
    # def should_poll(self):
    #     """No polling needed."""
    #     return False

    def update(self):
        """Get the latest data and update the states."""
        ip_addr,result = self._aliddns.do()
        if result:
            self._state = 'updated'
        else:
            self._state = 'not updated'
            
        self._attributes['ip'] = ip_addr
        self._attributes['updated'] = result
        self._attributes['domain'] = self._domain
        self._attributes['sub_domain'] = self._sub_domain

        _LOGGER.info(ip_addr)
        _LOGGER.info('update at aliyun ddns sensor')


