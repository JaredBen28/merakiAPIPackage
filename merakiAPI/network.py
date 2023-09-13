from typing import Union
from .merakiObject import _MerakiObject
from .device import Device
from .productTypes import _Appliance, _Camera, _Sensor, _Switch, _Wireless

class Network(_MerakiObject):
    def __init__(self, apiKey: str, organizationId: str = None, name: str = None, id: str = None) -> None:
        """ init network object, to init you need the orgId and name or network id, if all 3 are blank you will need to create a network

        Args:
            apiKey (str): api key of user
            organizationId (str, optional): organization id of network. Defaults to None.
            name (str, optional): name of network. Defaults to None.
            id (str, optional): id of network. Defaults to None.
        """
        super().__init__(apiKey)
        
        if name == None and id == None:
            if organizationId == None: return
            else: self.organizationId = organizationId
        else:
            if organizationId != None and name != None:
                self.organizationId = organizationId
                self.__getNetwork(name=name)
            elif id != None:
                self.__getNetwork(id=id)
            
            self.__getDevices()
            
    def __repr__(self):
        return "Name: %s, ID: %s, Product Types: [%s]" % (self.name, self.id, ','.join(self.productTypes))
    
    # ------------- Network ------------- #
    def __getNetwork(self, id: str = None, name: str = None) -> None:
        """ gets the network object from id or orgId and name

        Args:
            id (str, optional): id of network. Defaults to None.
            name (str, optional): name of network. Defaults to None.
        """
        if id != None: 
            endpoint = 'networks/%s' % id
        else: 
            endpoint = 'organizations/%s/networks' % self.organizationId
            
        statusCode, response = self.apiCall(endpoint, self._apiKey)
        if statusCode != 200: return None
        
        for network in response:
            if name == network['name']:
                self.name = network['name']
                self.id = network['id']
                self.productTypes = network['productTypes']
                self.timeZone = network['timeZone']
                self.tags = network['tags']
                self.url = network['url']
                self.notes = network['notes']
                
        if 'appliance' in self.productTypes: self.appliance = _Appliance(self._apiKey, self.id)
                
    def createNetwork(self, name: str, product_types: list[str], 
                      timezone: str = "America/New_York", 
                      tags: str = None, notes: str = "") -> str:
        """ creates a new network in organization

        Args:
            name (str): name of the network. Defaults to None.
            product_types (list[str]): product types of network: options ('appliance', 'camera', 'sensor', 'switch', 'wireless')
            timezone (str, optional): timezone of network. Defaults to "America/New_York".
            tags (str, optional): tags of network. Defaults to None.
            notes (str, optional): additional notes for network. Defaults to "".

        Returns:
            str: id of network
        """
        endpoint = 'organizations/%s/networks' % self.organizationId

        payload = {
            "name": name,
            "productTypes": product_types,
            "timezone": timezone,
            "tags": tags,
            "notes": notes\
        }
        
        statusCode, response = self.apiCall(endpoint, payload, 'POST')
        if statusCode != 200 and statusCode != 201: return
        
        self.name = response['name']
        self.id = response['id']
        self.productTypes = response['productTypes']
        self.timeZone = response['timeZone']
        self.tags = response['tags']
        self.url = response['url']
        self.notes = response['notes']

        print(f"Created network {self.name} with id {response['id']}")
        if 'appliance' in self.productTypes: self.appliance = _Appliance(self._apiKey, self.id)
        return self.id
                
    # ------------- Templates ------------- #      
    def getTemplateNames(self) -> list:
        """ gets a list of template names in org

        Returns:
            list: list of template names
        """
        endpoint = 'organizations/%s/configTemplates' % self.organizationId
     
        statusCode, response = self.apiCall(endpoint)
        if statusCode != 200: 
            return None
        
        return [t['name'] for t in response]
    
    def __getTemplateId(self, templateName: str) -> str:
        """ gets template id from name

        Args:
            templateName (str): name of the template

        Returns:
            str: id of template
        """
        endpoint = 'organizations/%s/configTemplates' % self.organizationId
     
        statusCode, response = self.apiCall(endpoint)
        if statusCode != 200: 
            return
        
        for t in response:
            if templateName == t['name']:
                return t['id']
    
    def bindTemplate(self, templateName: str, autoBind: bool = False) -> None:
        """ bind the network to a template

        Args:
            templateName (str): name of template to bind to
            autoBind (bool, optional): not sure but its a setting. Defaults to False.
        """
        if self.id == None:
            print('No id found')
            return
        
        endpoint = f'networks/{self.id}/bind'
     
        payload = {
            "configTemplateId": self.__getTemplateId(templateName),
            "autoBind": autoBind
        }
        
        status_code, _ = self.apiCall(endpoint, payload, 'POST')
        if status_code != 200:
            print('Did not Bind')
    
    def unbindTemplate(self, retainConfigs: bool = True) -> None:
        """ unbinds the network from its template

        Args:
            retainConfigs (bool, optional): Should you retain the configs from the template. Defaults to True.
        """
        endpoint = f'networks/{self.id}/unbind'
     
        payload = {"retainConfigs": retainConfigs}
        
        status_code, _ = self.apiCall(endpoint, payload, 'POST')
        if status_code != 200:
            print('Did not unbind')

    def bindAndUnbindTemplate(self, templateName: str, autoBind: bool = False) -> None:
        """ loads the unbinds a template, keeping the config

        Args:
            templateName (str): name of template to bind to
            autoBind (bool, optional): not sure, it's a setting. Defaults to False.
        """
        self.bindTemplate(templateName, autoBind)    
        self.unbindTemplate()
        if 'appliance' in self.productTypes: self.appliance = _Appliance(self._apiKey, self.id)
    
    # ------------- Appliance ------------- # -- Tested
    def getVlans(self) -> list:
        """ Gets the appliance VLANs

        Returns:
            list: list of vlan objects
        """
        if hasattr(self.appliance, 'vlans'):
            return self.appliance.vlans
        
    def getEnabled(self) -> bool:
        """ gets enabled status of VLAN

        Returns:
            bool: True or False
        """
        return self.appliance.vlansEnabled
        
    def enableVLANs(self) -> None: 
        """ enables the VLANs on the network
        """
        self.appliance.enableVLANs()
    
    def createVLAN(self, name: str, id: int, applianceIp: str, subnet: str, additionalOptions: dict = None) -> None:
        """ creates new VLAN

        Args:
            name (str): name of VLAN
            id (int): id of the VLAN 0 - 4096
            applianceIp (str): appliance IP of VLAN ex: 10.10.10.1
            subnet (str): subnet of VLAN ex: 10.10.10.0/24
            additionalOptions (dict, optional): any other options found in API documentation. Defaults to None.
        """
        self.appliance.createVLAN(name, id, applianceIp, subnet, additionalOptions)
        
    def changeVLANOctet(self, octet: int, newValue: int, name: str = None, id: int = None, allVLANs=False) -> None:
        """ changes the octet of a VLAN

        Args:
            octet (int): octet to change (1, 2, 3, 4)
            newValue (int): new value of the oct (0 - 255)
            name (str, optional): name of the VLAN to change. Defaults to None.
            id (int, optional): id of the VLAN to change. Defaults to None.
        """
        if allVLANs:
            for vlan in self.appliance.vlans:
                vlan.changeOctet(octet, newValue)
            return
        
        if name == None and id == None: return
        for vlan in self.appliance.vlans:
            if vlan.name == name or vlan.id == id:
                vlan.changeOctet(octet, newValue)
    
    def updateVLAN(self, payload: dict, name: str = None, id: int = None) -> None:
        """ updates a VLAN based on dict

        Args:
            payload (dict): options from meraki api documentation
            name (str, optional): name of the VLAN to change. Defaults to None.
            id (int, optional): id of the VLAN to change. Defaults to None.
        """
        if name == None and id == None: return
        for vlan in self.appliance.vlans:
            if vlan.name == name or vlan.id == id:
                vlan.update(payload)
                
    def getVLANReservedIpRanges(self, name: str = None, id: int = None) -> list[dict]:
        """ gets the reserved ip ranges of VLAN

        Args:
            name (str, optional): name of vlan. Defaults to None.
            id (int, optional): id of vlan. Defaults to None.

        Returns:
            list[dict]: list of reserved range dicts
        """
        if name == None and id == None: return
        for vlan in self.appliance.vlans:
            if vlan.name == name or vlan.id == id:
                return vlan.getReservedIpRanges()

    def reserveVLANIpRange(self, start: str, end: str, comment: str = 'comment', name: str = None, id: int = None, keepOld: bool = True) -> None:
        """ reserves an ip range in VLAN

        Args:
            start (str): start of the ip range ex: 10.10.10.20
            end (str): end of the ip range ex: 10.10.10.240
            comment (str, optional): comment of the range. Defaults to 'comment'.
            name (str, optional): name of the VLAN to change. Defaults to None.
            id (int, optional): id of the VLAN to change. Defaults to None.
        """
        if name == None and id == None: return
        for vlan in self.appliance.vlans:
            if vlan.name == name or vlan.id == id:
                vlan.reserveIpRange(start, end, comment, keepOld)
    
    def changeVLANOctetAndKeepRanges(self, octet: int, newValue: int, name: str = None, id: int = None, allVLANs=False) -> None:
        """ changes the octet and reserved ranges of a VLAN

        Args:
            octet (int): _description_
            newValue (int): _description_
            name (str, optional): _description_. Defaults to None.
            id (int, optional): _description_. Defaults to None.
            allVLANs (bool, optional): _description_. Defaults to False.
        """
        if allVLANs:
            for vlan in self.appliance.vlans:
                vlan.changeOctetAndRanges(octet, newValue)
            return
        
        if name == None and id == None: return
        for vlan in self.appliance.vlans:
            if vlan.name == name or vlan.id == id:
                vlan.changeOctetAndRanges(octet, newValue)
                
    def getL3FirewallRules(self):
        """ Get Layer 3 firewall rules of appliance

        Returns:
            _L3Firewall: layer 3 firewall object
        """
        return self.appliance.firewall.rules            
    
    def addL3FirewallRule(self, policy: str = 'deny', protocol: str = 'any',
                            srcPort: Union[int, str] = 'any', srcCidr: list[str] = 'any',
                            destPort: Union[int, str] = 'any', destCidr: list[str] = 'any',
                            comment: str = '', syslog: bool = False):
        """ adds a new l3 firewall rule to network

        Args:
            policy (str, optional): 'allow' or 'deny'. Defaults to 'deny'.
            protocol (str, optional): The type of protocol (must be 'tcp', 'udp', 'icmp', 'icmp6' or 'any'). Defaults to 'any'.
            srcPort (Union[int, str], optional): Comma-separated list of source port(s) (integer in the range 1-65535), or 'any'. Defaults to 'any'.
            srcCidr (list[str], optional): Comma-separated list of source IP address(es) (in IP or CIDR notation), or 'any' (note: FQDN not supported for source addresses). Defaults to 'any'.
            destPort (Union[int, str], optional): Comma-separated list of destination port(s) (integer in the range 1-65535), or 'any'. Defaults to 'any'.
            destCidr (list[str], optional): Comma-separated list of destination IP address(es) (in IP or CIDR notation), fully-qualified domain names (FQDN) or 'any'. Defaults to 'any'.
            comment (str, optional): Description of the rule. Defaults to ''.
            syslog (bool, optional):  only applicable if a syslog has been configured (optional). Defaults to False.

        Returns:
            _L3Firewall: layer 3 firewall object
        """
        
        print(destPort)
        self.appliance.firewall.addl3FirewallRule(policy, protocol, srcPort, srcCidr, destPort, destCidr, comment, syslog)
        return self.appliance.firewall.rules
                
    # ------------- Cameras ------------- #
    def getVideoLink(self, serial: str) -> str: # not tested
        """ gets the link to camera video stream

        Args:
            serial (str): serial of camera

        Returns:
            str: url of camera video steam
        """
        for camera in self.cameras:
            if camera.serial == serial:
                return camera.getVideoLink()
            
    def getAnalyticsOverview(self, serial: str = None) -> list[dict]: # not tested
        """ gets the analytics overview of camera

        Args:
            serial (str, optional): if not set, gets all cameras analytics overview. Defaults to None.

        Returns:
            list[dict]: list of the analytics overview
        """
        if serial == None:
            return [camera.getAnalyticsOverview() for camera in self.cameras]
        for camera in self.cameras:
            if camera.serial == serial:
                return camera.getAnalyticsOverview()
    
    # ------------- Devices ------------- #
    def getDevice(self, serial: str):
        """ Gets a device in network based on serial

        Args:
            serial (str): serial of device

        Returns:
            Object: Object of device
        """
        if 'camera' in self.productTypes:
            for camera in self.cameras:
                if camera.serial == serial:
                    return camera
        if 'sensor' in self.productTypes:
            for sensor in self.sensors:
                if sensor.serial == serial:
                    return sensor
        if 'switch' in self.productTypes:
            for switch in self.switches:
                if switch.serial == serial:
                    return switch
        if 'wireless' in self.productTypes:
            for wireless in self.wireless:
                if wireless.serial == serial:
                    return wireless
                
    def __getDevices(self) -> list:
        endpoint = 'networks/%s/devices' % self.id
        
        statusCode, response = self.apiCall(endpoint)
        _devices, _cameras, _sensors, _wireless, _switches = [], [], [], [], []

        for device in response:
            if 'MV' in device['model']:
                _cameras.append(_Camera(self._apiKey, device['serial'], payload=device))
            elif 'MT' in device['model']:
                _sensors.append(_Sensor(self._apiKey, device['serial'], payload=device))
            elif 'MR' in device['model']:
                _wireless.append(_Wireless(self._apiKey, device['serial'], payload=device))
            elif 'MS' in device['model']:
                _switches.append(_Switch(self._apiKey, device['serial'], payload=device))
            else:
                _devices.append(Device(self._apiKey, device['serial']))

        if 'camera' in self.productTypes: self.cameras = _cameras
        if 'sensor' in self.productTypes: self.sensors = _sensors
        if 'wireless' in self.productTypes: self.wireless = _wireless
        if 'switch' in self.productTypes: self.switches = _switches
        
    
    def claimDevices(self, serials: list[str]) -> None:
        """ claim a list of devices

        Args:
            serials (list[str]): list of all serials to claim
        """
        endpoint = 'networks/%s/devices/claim' % self.id
        payload = {
                "serials" : serials
            }
        
        statusCode = self._apiJsonErrorCall(endpoint, payload)
        
        if statusCode == 200: 
            print('Devices Claimed')
        else:
            print('Device not in organization; error:', statusCode)
    
    def updateDevice(self, update: dict, serials: list[str]):
        """ update a list of devices

        Args:
            update (dict): payload for the update, use the meraki api documentation
            serials (list[str]): list of serials update
        """
        
        for device in self.cameras + self.sensors + self.wireless + self.switches:
            if serials is None or device.serial in serials:
                device.update(update)
                
    def updateLocation(self, address: str, serials: list[str]):
        """ update the location of a list of devices

        Args:
            address (str): new location
            serials (list[str]): list of serials to update
        """
        for device in self.cameras + self.sensors + self.wireless + self.switches:
            if serials is None or device.serial in serials:
                device.update({'address': address})
                
    def removeDevice(self, serials: list[str]):
        """ remove a list of devices

        Args:
            serials (list[str]): list of serials to remove
        """
        endpoint = 'networks/%s/devices/remove' % self.id
        for serial in serials:
            payload = {"serial": serial}
            
            statusCode = self._apiJsonErrorCall(endpoint, payload)
            
            if statusCode == 204:
                print('Device removed from network')
            else:
                print('Device not in network; error:', statusCode)
            
        self.devices = self.__getDevices()
                
    # ------------- Sensors ------------- #

    def getSensorMetrics(self, serial: str = None):
        """ gets the metric of sensor

        Args:
            serial (str, optional): serial to get metrics, if None gets all sensors. Defaults to None.

        Returns:
            list[dict] or dict: metrics
        """
        if serial == None:
            return [sensor.getMetrics() for sensor in self.sensors]

        for sensor in self.sensors:
            if sensor.serial == serial:
                return sensor.getMetrics()    
    
    # ------------- Switches ------------- #
    def getSwitch(self, serial: str):
        """ gets a switch object based on serial

        Args:
            serial (str): serial of switch

        Returns:
            Switch Object: switch object
        """
        for switch in self.switches:
            if switch.serial == serial:
                return switch
            
    def getTrunkPorts(self, serial: str = None) -> list[str]:
        """ gets trunk ports of a switch

        Args:
            serial (str, optional): Switch serial, if None gets all. Defaults to None.

        Returns:
            list[str]: list of trunk port ids
        """
        if serial == None:
            return [switch.getTrunkPorts() for switch in self.switches]
        
        for switch in self.switches:
            if switch.serial == serial:
                return switch.getTrunkPorts()
            
    def changePortType(self, serial: str, portId: str, portType: str) -> str: 
        """ Changes the port type

        Args:
            serial (str): serial of switch of port
            portId (str): port id to change
            portType (str): 'access' or 'trunk'

        Returns:
            str: message if success
        """
        for switch in self.switches:
            if switch.serial == serial:
                if portType == 'access': 
                    return switch.changePortToAccess(portId)
                elif portType == 'trunk':
                    return switch.changePortToTrunk(portId)
    
    def updatePortVlan(self, serial: str, portId: str, newVlan: int) -> None:
        """ Update the VLAN of a port

        Args:
            serial (str): serial of switch of port
            portId (str): port id to change
            newVlan (int): _description_

        Returns:
            str: message if success
        """
        for switch in self.switches:
            if switch.serial == serial:
                return switch.updatePortVlan(portId, newVlan)
    
    def getSwitchClients(self, serial: str, trunkPorts: list[str] = []) -> list[dict]:
        """ get clients of switch

        Args:
            serial (str): switch of serial
            trunkPorts (list[str], optional): List of trunk ports to filter out, if needed. Defaults to [].

        Returns:
            list[dict]: list of clients
        """
        for switch in self.switches:
            if switch.serial == serial:
                return switch.getClients(trunkPorts)
            
    def updateSwitchPort(self, serial: str, portId: str, payload: dict) -> None:
        """ Updates a switch port

        Args:
            serial (str): serial of switch
            portId (str): port id to change
            payload (dict): payload based on meraki api documentation

        Returns:
            str: message if success
        """
        for switch in self.switches:
            if switch.serial == serial:
                return switch.updatePort(portId, payload)
    
    # ------------- Wireless ------------- #
    def getWireless(self, serial: str):
        """ gets a wireless device

        Args:
            serial (str): serial of wireless device

        Returns:
            Wireless Object: wireless object for serial
        """
        for wireless in self.wireless:
            if serial == wireless.serial:
                return wireless
    
    def getSSIDs(self, serial: str):
        """ get all ssid object of wireless device

        Args:
            serial (str): serial of wireless device

        Returns:
            list of SSID Objects: list of ssid objects for switch
        """
        for wireless in self.wireless:
            if serial == wireless.serial:
                return wireless.ssids
    
    def getSSID(self, serial: str, number: int = None, name: str = None):
        """ gets an ssid of switch, need number or name to get ssid

        Args:
            serial (str): serial of switch 
            number (int, optional): number of ssid 0-15. Defaults to None.
            name (str, optional): name of ssid. Defaults to None.

        Returns:
            SSID Object: SSID object 
        """
        for wireless in self.wireless:
            if serial == wireless.serial:
                for ssid in wireless.ssids:
                    if (ssid.number == number or number == None) and (ssid.name == name or name == None):
                        return ssid
    
    def updateSSID(self, serial: str, payload: dict, number: int = None, name: str = None) -> str:
        """ updates an SSID of switch, need number or name to get ssid

        Args:
            serial (str): serial of switch
            payload (dict): payload based on meraki api documentation
            number (int, optional): number of ssid 0-15. Defaults to None.
            name (str, optional): name of ssid. Defaults to None.

        Returns:
            str: success message
        """
        for wireless in self.wireless:
            if serial == wireless.serial:
                for ssid in wireless.ssids:
                    if (ssid.number == number or number == None) and (ssid.name == name or name == None):
                        return ssid.update(payload)
    
    def changeSSIDVLAN(self, serial: str, newVlanId: str, number: int = None, name: str = None) -> str: # Questionable
        """ changes the vlan of an ssid, need number or name to get ssid

        Args:
            serial (str): serial of switch
            newVlanId (str): new vlan id of ssid
            number (int, optional): number of ssid 0-15. Defaults to None.
            name (str, optional): name of ssid. Defaults to None.

        Returns:
            str: success message
        """
        for wireless in self.wireless:
            if serial == wireless.serial:
                for ssid in wireless.ssids:
                    if (ssid.number == number or number == None) and (ssid.name == name or name == None):
                        return ssid.changeVlan(newVlanId)
    
    def changeSSIDPSK(self, serial: str, psk: str, number: int = None, name: str = None) -> str: # Questionable
        """ changes the psk of ssid, need number or name to get ssid

        Args:
            serial (str): serial of switch
            psk (str): new pass key of ssid
            number (int, optional): number of ssid 0-15. Defaults to None.
            name (str, optional): name of ssid. Defaults to None.

        Returns:
            str: success message
        """
        for wireless in self.wireless:
            if serial == wireless.serial:
                for ssid in wireless.ssids:
                    if (ssid.number == number or number == None) and (ssid.name == name or name == None):
                        return ssid.changePSK(psk)
                
    def changeSSIDName(self, serial: str, newName: str, number: int = None, name: str = None) -> str:
        """ changes the ssid name, need number or name to get ssid

        Args:
            serial (str): serial of switch
            newName (str): new same of ssid
            number (int, optional): number of ssid 0-15. Defaults to None.
            name (str, optional): name of ssid. Defaults to None.

        Returns:
            str: success message
        """
        for wireless in self.wireless:
            if serial == wireless.serial:
                for ssid in wireless.ssids:
                    if (ssid.number == number or number == None) and (ssid.name == name or name == None):
                        return ssid.changeName(newName)
                        
    def enableSSID(self, serial: str, number: int = None, name: str = None) -> str:
        """ enables ssid, need number or name to get ssid

        Args:
            serial (str): serial of switch
            number (int, optional): number of ssid 0-15. Defaults to None.
            name (str, optional): name of ssid. Defaults to None.

        Returns:
            str: success message
        """
        for wireless in self.wireless:
            if serial == wireless.serial:
                for ssid in wireless.ssids:
                    if (ssid.number == number or number == None) and (ssid.name == name or name == None):
                        return ssid.enable()
                        
    def disableSSID(self, serial: str, number: int = None, name: str = None) -> str:
        """ disables ssid, need number or name to get ssid

        Args:
            serial (str): serial of switch
            number (int, optional): number of ssid 0-15. Defaults to None.
            name (str, optional): name of ssid. Defaults to None.

        Returns:
            str: success message
        """
        for wireless in self.wireless:
            if serial == wireless.serial:
                for ssid in wireless.ssids:
                    if (ssid.number == number or number == None) and (ssid.name == name or name == None):
                        return ssid.disable()