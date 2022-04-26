#!/usr/bin/env python3
"""
This is a NodeServer for Onkyo Receivers of the TX-NR varieties
by steveng57 (Steven Goulet: steven.goulet@live.com)

"""

import sys
import time
import json
from onkyoapi import OnkyoReceiver
import udi_interface

LOGGER = udi_interface.LOGGER

VERSION = '1.0.2'

class Controller(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name):
        super(Controller, self).__init__(polyglot, primary, address, name)
        self.name = 'Onkyo Controller'
        self.address = address
        self.poly = polyglot
        self.ipaddress = ''
        self.port = 60128
        self.configured = False
        
        polyglot.subscribe(polyglot.START, self.start, address)
        polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)

        polyglot.ready()
        polyglot.addNode(self, conn_status="ST")

    def parameterHandler(self, params):
        valid = True
        self.poly.Notices.clear()

        if 'ipaddress' in params and params['ipaddress'] != '':
            self.ipaddress = params['ipaddress']
        else:
            valid = False
            self.poly.Notices['ip'] = "Please enter the IP address of the Onkyo receiver."

        if 'port' in params and params['port'] != '':
            self.port = int(params['port'])
        else:
            valid = False
            self.poly.Notices['port'] = "Please enter the port for the Onkyo receiver."

        if valid:
            self.discover()
            self.configured = True
            

    def start(self):
        LOGGER.info('Starting Onkyo Polyglot v2 NodeServer version {}, udi_interface: {}'.format(VERSION, udi_interface.__version__))
        self.poly.updateProfile()
        
        while not self.configured:
            time.sleep(1)
            
        LOGGER.info('Creating OnkyoReceiver API object with ipaddress={} and port={}'.format(self.ipaddress, self.port))
        self.OnkyoReceiver = OnkyoReceiver(self.ipaddress, self.port)

    def query(self):
        self.reportDrivers()

    def discover(self, *args, **kwargs):
        LOGGER.info('Adding Onkyo Zone Nodes to {}...Main, Zone 2, Zone 3'.format(self.address))

        if not self.poly.getNode('main'):
            self.poly.addNode(ZoneNode(self.poly, self.address, 'main', 'main', 1))        
        if not self.poly.getNode('zone2'):
            self.poly.addNode(ZoneNode(self.poly, self.address, 'zone2', 'zone2', 2))        
        if not self.poly.getNode('zone3'):
            self.poly.addNode(ZoneNode(self.poly, self.address, 'zone3', 'zone3', 3))

    def delete(self):
        LOGGER.info('Node server deleted')

    def stop(self):
        LOGGER.debug('Node Server stopped.')

    id = 'controller'
    commands = { }
    drivers = [{'driver': 'ST', 'value': 0, 'uom': 25}]



class ZoneNode(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name, zoneId):

        self.parent = polyglot.getNode(primary)

        self.zondId = zoneId
        LOGGER.info('Added Onkyo Zone: {}'.format(name))
        super(ZoneNode, self).__init__(polyglot, primary, address, name)


    def _PowerOn(self, command):
        self.parent.OnkyoReceiver.On(self.zondId)
        self.setDriver('ST', 1)

    def _PowerOff(self, command):
        self.parent.OnkyoReceiver.Off(self.zondId)
        self.setDriver('ST', 0)

    def _Volume(self, command):
        try:
            val = int(command.get('value'))
        except:
            LOGGER.error('volume: Invalid argument')
        else:
            self.volume = val
            self.parent.OnkyoReceiver.Set(self.zondId, val)
            self.setDriver('SVOL', val)

    def _Mute(self, command):
        self.mute = True
        self.parent.OnkyoReceiver.Mute(self.zondId)
        self.setDriver('GV0', 1)

    def _UnMute(self, command):
        self.parent.OnkyoReceiver.UnMute(self.zondId)
        self.mute = False
        self.setDriver('GV0', 0)

    def query(self):
        self.reportDrivers()

    drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 2},  # zone On/off
            {'driver': 'SVOL', 'value': 0, 'uom': 51},  # zone volume
            {'driver': 'GV0', 'value': 0, 'uom': 2}  # zone mute state
            ]
    id = 'onkyozone'

    commands = {
                    'VOLUME': _Volume,
                    'MUTE': _Mute,
                    'UNMUTE': _UnMute,
                    'POWERON': _PowerOn, 
                    'POWEROF': _PowerOff
                }

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start(VERSION)
        Controller(polyglot, 'controller', 'controller', 'Onkyo')
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)

