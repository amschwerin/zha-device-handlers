"""Viconics VT8000"""
import logging

from zigpy.profiles import zha
from zigpy.quirks import CustomCluster, CustomDevice

from zigpy.zcl.clusters.general import (
    Basic,
    Groups,
    Identify,
    Ota,
    Scenes,
)
from zigpy.zcl.clusters.hvac import (
    Thermostat,
    Fan,
    UserInterface,
)
from zigpy.zcl.clusters.measurement import (
    TemperatureMeasurement,
    OccupancySensing,
)
from zigpy.zcl.clusters.security import (
    IasZone,
)
from ..const import (
    DEVICE_TYPE,
    ENDPOINTS,
    INPUT_CLUSTERS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
)

_LOGGER = logging.getLogger(__name__)

class TemperatureFixer(object):
    """Type to mix into custom devices that need to fix up temperature attributes
    that the device incorrectly double-converted from imperial to si units.
    
    For these problematic attributes, if trueC is the temperature they're trying
    to report in degrees Celsius report convertFtoC(trueC).

    To use this type, mix it into a custom device type, and create a class level
    list of broken attributes by name, called "temperature_applicable_attributes".
    """
    def fix_value(self, attrid, value):
        """Function provided to fix temperature attributes."""
        attr_info = self.attributes.get(attrid, ("", ))
        _LOGGER.debug("Processing fix_value for attrid 0x%x %s", attrid, attr_info)
        if attr_info[0] not in self.temperature_applicable_attributes:
            return value
        _LOGGER.debug("Converting from value %s", value)
        return attr_info[1](value * 9.0 / 5.0 + 3200)

class FixTemperatureCluster(CustomCluster, TemperatureMeasurement, TemperatureFixer):
    """Custom Temperature cluster that fixes misreported temperatures."""
    cluster_id = TemperatureMeasurement.cluster_id
    temperature_applicable_attributes = [
        "measured_value",
        "min_measured_value",
        "max_measured_value",
    ]

    def _update_attribute(self, attrid, value):
        _LOGGER.debug("Updating attribute in FixTemperatureCluster 0x%x %s", attrid, value)
        super()._update_attribute(attrid, self.fix_value(attrid, value))


class VT8000(CustomDevice):
    """Viconics VT8000 HVAC Controller"""

    signature = {
        MODELS_INFO: [("Viconics", "8000 SERIES")],
        ENDPOINTS: {
            10: {
                PROFILE_ID: 0x104,
                DEVICE_TYPE: zha.DeviceType.THERMOSTAT,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    Thermostat.cluster_id,
                    Fan.cluster_id,
                    UserInterface.cluster_id,
                    TemperatureMeasurement.cluster_id,
                    OccupancySensing.cluster_id,
                ],
                OUTPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    Thermostat.cluster_id,
                    Fan.cluster_id,
                    UserInterface.cluster_id,
                    TemperatureMeasurement.cluster_id,
                    OccupancySensing.cluster_id,
                    IasZone.cluster_id,
                ],
            },
            14: {
                PROFILE_ID: 0x104,
                DEVICE_TYPE: zha.DeviceType.ON_OFF_SWITCH,
                INPUT_CLUSTERS: [],
                OUTPUT_CLUSTERS: [
                    Ota.cluster_id,
                ],
            },
        },
    }

    replacement = {
        ENDPOINTS: {
            10: {
                PROFILE_ID: 0x104,
                DEVICE_TYPE: zha.DeviceType.THERMOSTAT,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    Thermostat.cluster_id,
                    Fan.cluster_id,
                    UserInterface.cluster_id,
                    FixTemperatureCluster,
                    OccupancySensing.cluster_id,
                ],
                OUTPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    Thermostat.cluster_id,
                    Fan.cluster_id,
                    UserInterface.cluster_id,
                    FixTemperatureCluster,
                    OccupancySensing.cluster_id,
                    IasZone.cluster_id,
                ],
            },
            14: {
                PROFILE_ID: 0x104,
                DEVICE_TYPE: zha.DeviceType.ON_OFF_SWITCH,
                INPUT_CLUSTERS: [],
                OUTPUT_CLUSTERS: [
                    Ota.cluster_id,
                ],
            },
        }
    }
