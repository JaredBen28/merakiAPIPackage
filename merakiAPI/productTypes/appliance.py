import json
from typing import Union
from ..device import Device
from ..merakiObject import _MerakiObject

class _Appliance(_MerakiObject):
    def __init__(self, apiKey: str, networkId: str) -> None:
        super().__init__(apiKey)
        self.networkId = networkId
        self.firewall = _L3Firewall(apiKey, self.networkId)
        self.vlansEnabled = self.getVLANsEnabled()

        if self.vlansEnabled: 
            self.vlans = self.__getVLANs()
        
    
    def __getVLANs(self) -> list:
        endpoint = 'networks/%s/appliance/vlans' % self.networkId
        
        statusCode, response = self.apiCall(endpoint)
        if statusCode != 200: return
        
        return [_VLAN(self._apiKey, self.networkId, vlan['id']) for vlan in response] 
    
    def enableVLANs(self) -> None:
        if self.vlansEnabled: return
        
        endpoint = 'networks/%s/appliance/vlans/settings' % self.networkId
        payload = {"vlansEnabled": True}
        
        statusCode, _ = self.apiCall(endpoint, payload, 'PUT')
        if statusCode != 200: 
            print('VLANs not enabled')
            self.vlansEnabled = False
        
        self.vlansEnabled = True
        self.vlans = self.__getVLANs()
    
    def getVLANsEnabled(self):
        endpoint = 'networks/%s/appliance/vlans/settings' % self.networkId
        
        statusCode, response = self.apiCall(endpoint)
        if statusCode != 200: self.vlans = None
        else:
            return response['vlansEnabled'] 

    def createVLAN(self, name: str, id: int, applianceIp: str, subnet: str, additionalOptions: dict = None) -> None:
        """ Creates a new VLAN 

        Args:
            name (str): Name of VLAN
            id (int): ID of VLAN (1-4096)
            applianceIp (str): appliance IP of VLAN ex: 192.168.10.1 
            subnet (str): Subnet of VLAN ex: 192.168.10.0/24
            additionalOptions (dict, optional): _description_. Defaults to {}.

        Returns:
            None
        """
        endpoint = 'networks/%s/appliance/vlans' % self.networkId
        
        payload = {
            'name': name,
            'id': id,
            'subnet': subnet,
            'applianceIp': applianceIp,
        }
        
        if additionalOptions != None:
            payload |= additionalOptions
            
        statusCode, response = self.apiCall(endpoint, payload, 'POST')
        if statusCode != 201:
            print('VLAN could not be created')
            return None
        
        if hasattr(self, 'vlans'):
            self.vlans.append(_VLAN(self._apiKey, self.networkId, response['id']))
        else:
            self.vlans = _VLAN(self._apiKey, self.networkId, response['id'])
        
        
class _VLAN(_MerakiObject):
    def __init__(self, apiKey: str, networkId: str, id: int = None) -> None:
        super().__init__(apiKey)
        self.networkId = networkId
        self.id = id
        vlan = self.__get()
        self.name = vlan['name']
        self.subnet = vlan['subnet']
        self.applianceIp = vlan['applianceIp']
        self.additionalOptions = {k : v for k, v in vlan.items() if k not in ['name', 'subnet', 'applianceIp']}
    
    def __repr__(self) -> str:
        return "Id: %i, Name: %s, Subnet: %s, Appliance IP: %s" % (self.id, self.name, self.subnet, self.applianceIp)
    
    def __get(self) -> dict:
        endpoint = 'networks/%s/appliance/vlans/%s' % (self.networkId, self.id)
        statusCode, response = self.apiCall(endpoint)
        
        if statusCode != 200:
            print('Could not get VLAN')
            return None
        
        return response
        
    def delete(self) -> None:
        """ Deletes this VLAN
        """
        endpoint = 'networks/%s/appliance/vlans/%s' % (self.networkId, self.id)
        response = self._delete(endpoint)
        print(response.status_code)
    
    def update(self, payload: dict) -> dict:
        """ update vlan configs

        Args:
            payload (dict): update for vlan

        Returns:
            dict: new vlan configs
        """
        endpoint = 'networks/%s/appliance/vlans/%s' % (self.networkId, self.id)
        return self.apiCall(endpoint, payload, 'PUT')
    
    def changeOctet(self, octetToChange: int, newValue: int) -> None:
        endpoint = 'networks/%s/appliance/vlans/%s' % (self.networkId, self.id)
        
        applianceIp = self.applianceIp.split('.')
        applianceIp[octetToChange-1] = str(newValue)
        newApplianceIp = '.'.join(applianceIp)
        
        subnet = self.subnet.split('.')
        subnet[octetToChange-1] = str(newValue)
        newSubnet = '.'.join(subnet)
        
        payload = {
            "applianceIp": newApplianceIp,
            "subnet": newSubnet
        }

        statusCode, response = self.apiCall(endpoint, payload, 'PUT')
        
        if statusCode != 200:
            print(response)
        else:
            self.applianceIp = newApplianceIp
            self.subnet = newSubnet
    
    def getReservedIpRanges(self) -> list[dict]: 
        print(self.additionalOptions['reservedIpRanges'])
        return self.additionalOptions['reservedIpRanges']
    
    def reserveIpRange(self, start: str, end: str, comment: str = "comment", keepOld=True) -> None:
        endpoint = 'networks/%s/appliance/vlans/%s' % (self.networkId, self.id)
        if 'reservedIpRanges' in self.additionalOptions.keys():
            _oldReservedIpRanges = self.additionalOptions['reservedIpRanges']
        
        newRange = {
            "start": start,
            "end": end,
            "comment": comment
        }
        
        payload = {
            'reservedIpRanges': _oldReservedIpRanges + [newRange]
        }        

        statusCode, response = self.apiCall(endpoint, payload, 'PUT')
        print(statusCode, response)
        if statusCode != 200:
            self.reservedIpRanges = _oldReservedIpRanges
            print('unable to reserve range\n' + response)
            
        self.additionalOptions['reservedIpRanges'] = response['reservedIpRanges']

    def changeOctetAndRanges(self, octetToChange: int, newValue: int) -> None:
        applianceIp = self.applianceIp.split('.')
        applianceIp[octetToChange-1] = str(newValue)
        newApplianceIp = '.'.join(applianceIp)
        
        subnet = self.subnet.split('.')
        subnet[octetToChange-1] = str(newValue)
        newSubnet = '.'.join(subnet)
        
        oldRanges = self.additionalOptions['reservedIpRanges']
        newRanges = []
        for range in oldRanges:
            newStart = range['start'].split('.')
            newStart[octetToChange-1] = str(newValue)
            newStart = '.'.join(newStart)
            
            newEnd = range['end'].split('.')
            newEnd[octetToChange-1] = str(newValue)
            newEnd = '.'.join(newEnd)
            
            newRanges.append({
                'start': newStart,
                'end': newEnd,
                'comment': range['comment']
            })
            
        payload = {
            "applianceIp": newApplianceIp,
            "subnet": newSubnet,
            "reservedIpRanges": newRanges
        }
        
        statusCode, response = self.update(payload)

class _L3Firewall(_MerakiObject):
    def __init__(self, apiKey, networkId) -> None:
        super().__init__(apiKey)
        self.networkId = networkId
        self.rules = self.__get()
    
    def __repr__(self) -> str:
        return str(self.rules)
    
    def __get(self) -> list[dict]:
        endpoint = 'networks/%s/appliance/firewall/l3FirewallRules' % self.networkId
        statusCode, response = self.apiCall(endpoint)
        
        if statusCode != 200:
            print('unable to get firewall rules')
            return None

        return response['rules']
    
    def addl3FirewallRule(self, policy: str = 'deny', protocol: str = 'any',
                            srcPort: Union[int, str] = 'any', srcCidr: list[str] = 'any',
                            destPort: Union[int, str] = 'any', destCidr: list[str] = 'any',
                            comment: str = '', syslog: bool = False):
        """ addl3FirewallRule
    
        Args:
            policy (str, optional): 'allow' or 'deny'. Defaults to 'deny'.
            protocol (str, optional): 'tcp', 'udp', 'icmp', 'icmp6', or 'any'. Defaults to 'any'.
            srcPort (Union[int, str], optional): _description_. Defaults to 'any'.
            srcCidr (list[str], optional): _description_. Defaults to 'any'.
            destPort (Union[int, str], optional): _description_. Defaults to 'any'.
            destCidr (list[str], optional): _description_. Defaults to 'any'.
            comment (str, optional): _description_. Defaults to ''.
            syslog (bool, optional): _description_. Defaults to False.
        """
        endpoint = 'networks/%s/appliance/firewall/l3FirewallRules' % self.networkId
        
        newRule = {
            "comment": comment,
            "policy": policy,
            "protocol": protocol,
            "destPort": destPort,
            "destCidr": destCidr,
            "srcPort": srcPort,
            "srcCidr": srcCidr,
            "syslogEnabled": syslog
        }
        
        payload = {'rules': self.rules + [newRule]}
        statusCode, response = self.apiCall(endpoint, payload, 'PUT')
        
        self.rules = self.__get()