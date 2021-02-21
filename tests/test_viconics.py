"""Tests of quirks for viconics."""

import zigpy.types as t

from zhaquirks.viconics import vt8000

def test_fix_value():
    """Test the mix-in type that fixes mis-reporting temperature attribute values."""

    class Temper(vt8000.TemperatureFixer):
        """The Temper class has a "misreporting" temperature attribute and another attribute to be ignored.
        """
        attributes = {
            0x00: ("temperature", t.int16s),
            0x01: ("region", t.int16s),
        }
        temperature_applicable_attributes = [ "temperature" ]
    
    temper = Temper()
    assert temper.fix_value(0x01, 100) == 100
    assert temper.fix_value(0x00, t.int16s(-111)) == t.int16s(3000)
    assert temper.fix_value(0x00, t.int32s(-111)) == t.int16s(3000)