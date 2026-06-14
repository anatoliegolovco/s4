from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

sintez2 = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'Z84C00', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Z84C00'}), 'ref_prefix':'D', 'fplist':None, 'footprint':'Package_DIP:DIP-40_W15.24mm', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='A11',func=pin_types.OUTPUT),
            Pin(num='2',name='A12',func=pin_types.OUTPUT),
            Pin(num='3',name='A13',func=pin_types.OUTPUT),
            Pin(num='4',name='A14',func=pin_types.OUTPUT),
            Pin(num='5',name='A15',func=pin_types.OUTPUT),
            Pin(num='6',name='CLK',func=pin_types.INPUT),
            Pin(num='7',name='D4',func=pin_types.BIDIR),
            Pin(num='8',name='D3',func=pin_types.BIDIR),
            Pin(num='9',name='D5',func=pin_types.BIDIR),
            Pin(num='10',name='D6',func=pin_types.BIDIR),
            Pin(num='11',name='VCC',func=pin_types.PWRIN),
            Pin(num='12',name='D2',func=pin_types.BIDIR),
            Pin(num='13',name='D7',func=pin_types.BIDIR),
            Pin(num='14',name='D0',func=pin_types.BIDIR),
            Pin(num='15',name='D1',func=pin_types.BIDIR),
            Pin(num='16',name='~INT',func=pin_types.INPUT),
            Pin(num='17',name='~NMI',func=pin_types.INPUT),
            Pin(num='18',name='~HALT',func=pin_types.OUTPUT),
            Pin(num='19',name='~MREQ',func=pin_types.TRISTATE),
            Pin(num='20',name='~IORQ',func=pin_types.TRISTATE),
            Pin(num='21',name='~RD',func=pin_types.TRISTATE),
            Pin(num='22',name='~WR',func=pin_types.TRISTATE),
            Pin(num='23',name='~BUSAK',func=pin_types.OUTPUT),
            Pin(num='24',name='~WAIT',func=pin_types.INPUT),
            Pin(num='25',name='~BUSRQ',func=pin_types.INPUT),
            Pin(num='26',name='~RESET',func=pin_types.INPUT),
            Pin(num='27',name='~M1',func=pin_types.OUTPUT),
            Pin(num='28',name='~RFSH',func=pin_types.OUTPUT),
            Pin(num='29',name='GND',func=pin_types.PWRIN),
            Pin(num='30',name='A0',func=pin_types.TRISTATE),
            Pin(num='31',name='A1',func=pin_types.TRISTATE),
            Pin(num='32',name='A2',func=pin_types.TRISTATE),
            Pin(num='33',name='A3',func=pin_types.TRISTATE),
            Pin(num='34',name='A4',func=pin_types.TRISTATE),
            Pin(num='35',name='A5',func=pin_types.TRISTATE),
            Pin(num='36',name='A6',func=pin_types.TRISTATE),
            Pin(num='37',name='A7',func=pin_types.TRISTATE),
            Pin(num='38',name='A8',func=pin_types.TRISTATE),
            Pin(num='39',name='A9',func=pin_types.TRISTATE),
            Pin(num='40',name='A10',func=pin_types.TRISTATE)] }),
        Part(**{ 'name':'Crystal', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'Crystal'}), 'ref_prefix':'Z', 'fplist':None, 'footprint':'Crystal:Crystal_HC49-U_Vertical', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'K1533LN1', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'K1533LN1'}), 'ref_prefix':'D', 'fplist':None, 'footprint':'Package_DIP:DIP-14_W7.62mm', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='1A',func=pin_types.INPUT),
            Pin(num='2',name='1Y',func=pin_types.OUTPUT),
            Pin(num='3',name='2A',func=pin_types.INPUT),
            Pin(num='4',name='2Y',func=pin_types.OUTPUT),
            Pin(num='5',name='3A',func=pin_types.INPUT),
            Pin(num='6',name='3Y',func=pin_types.OUTPUT),
            Pin(num='7',name='GND',func=pin_types.PWRIN),
            Pin(num='8',name='4Y',func=pin_types.OUTPUT),
            Pin(num='9',name='4A',func=pin_types.INPUT),
            Pin(num='10',name='5Y',func=pin_types.OUTPUT),
            Pin(num='11',name='5A',func=pin_types.INPUT),
            Pin(num='12',name='6Y',func=pin_types.OUTPUT),
            Pin(num='13',name='6A',func=pin_types.INPUT),
            Pin(num='14',name='VCC',func=pin_types.PWRIN)] }),
        Part(**{ 'name':'R', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'R'}), 'ref_prefix':'R', 'fplist':None, 'footprint':'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE),
            Pin(num='2',name='~',func=pin_types.PASSIVE)] }),
        Part(**{ 'name':'C', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'C'}), 'ref_prefix':'C', 'fplist':None, 'footprint':'Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm', 'keywords':None, 'description':'', 'datasheet':None, 'pins':[
            Pin(num='1',name='~',func=pin_types.PASSIVE),
            Pin(num='2',name='~',func=pin_types.PASSIVE)] })])