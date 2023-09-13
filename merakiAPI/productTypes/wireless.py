from ..merakiObject import _MerakiObject
from ..device import Device
import json

class _Wireless(Device):
    def __init__(self, apiKey, serial, payload: dict = None) -> None:
        super().__init__(apiKey, serial, True, payload = payload)
        self.ssids = self.__getSSIDs()
    
    def __getSSIDs(self) -> list:
        endpoint = 'networks/%s/wireless/ssids' % self.networkId
        
        statusCode, response = self.apiCall(endpoint)
        if statusCode != 200: return
        
        return [_SSID(self._apiKey, self.networkId, ssid) for ssid in response]
            
        
    def updateSSIDs(self, payload: dict, name: str = None, number: int = None) -> None:
        if name == None and number == None:
            print('No Name or Number')
            return
        elif number != None:
            pass
        elif name != None:
            number_ = [s.number for s in self.ssids if s.name == name]
            if len(number_) == 0:
                print('name not found')
                return
            else:
                number = number_[0]
        
        endpoint = 'networks/%s/wireless/ssids/%i' % (self.networkId, number)
        payload = payload
        
        statusCode, response = self.apiCall(endpoint, payload, 'PUT')
        
        
class _SSID(_MerakiObject):
    def __init__(self, apiKey, networkId, information) -> None:
        super().__init__(apiKey)
        keys = information.keys()

        self.networkId = networkId
        self.number = information['number']
        self.name = information['name']
        self.enabled = information['enabled']
        if 'psk' in keys: self.psk = information['psk']
        if 'defaultVlanId' in keys: self.defaultVlanId = information['defaultVlanId']
        self.additionalOptions = {k: v for k,v in information.items() if k not in ['name', 'number', 'enabled', 'psk', 'defaultVlanId']}
    
    def __repr__(self) -> str:
        return "SSID: %s, Number: %s, Enabled: %s" % (self.name, self.number, str(self.enabled))
            
    def getSSID(self):
        endpoint = 'networks/%s/wireless/ssids/%s' % (self.networkId, self.number)
        statusCode, response = self.apiCall(endpoint)
        keys = response.keys()
        
        self.number = response['number']
        self.name = response['name']
        self.enabled = response['enabled']
        if 'psk' in keys: self.psk = response['psk']
        if 'defaultVlanId' in keys: self.defaultVlanId = response['defaultVlanId']
        self.additionalOptions = {k: v for k, v in response.items() if k not in ['name', 'number', 'enabled', 'psk', 'defaultVlanId']}
    
    def enable(self) -> str:
        payload = {"enabled": True}
        return self.updateSSID(payload)
        
    def disable(self) -> str:
        payload = {"enabled": False}
        return self.updateSSID(payload)    
    
    def changeVlan(self, vlanId: int) -> str:
        payload = {"vlanId": vlanId}
        return self.updateSSID(payload)
        
    def changePSK(self, psk: str) -> str:
        if not hasattr(self, 'psk'): return
        
        payload = {"psk": psk}
        return self.updateSSID(payload)
        
    def changeName(self, name: str) -> str:
        payload = {"name": name}
        return self.updateSSID(payload)
        
    def updateSSID(self, payload) -> str:
        endpoint = 'networks/%s/wireless/ssids/%s' % (self.networkId, self.number)
        statusCode, response = self.apiCall(endpoint, payload, 'PUT')
        if statusCode != 200: return

        self.getSSID()
        return 'SSID updated'