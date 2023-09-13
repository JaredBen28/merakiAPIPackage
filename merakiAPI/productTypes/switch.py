from ..merakiObject import _MerakiObject
from ..device import Device
class _Switch(Device):
    def __init__(self, apiKey:str, serial: str, payload: dict = None) -> None:
        super().__init__(apiKey, serial, True, payload=payload)
        self.serial = serial
        self.ports = self.getPorts()
        self.portStatuses = self.getPortStatuses()
    
    def __repr__(self) -> str:
        return "Serial: %s, Name: %s" % (self.serial, self.name)
    
    def getPorts(self):
        endpoint = 'devices/%s/switch/ports' % self.serial
        statusCode, response = self.apiCall(endpoint)
        if statusCode != 200: return
        
        return  {port['portId']: port for port in response}
    
    def getPortStatuses(self):
        endpoint = 'devices/%s/switch/ports/statuses' % self.serial
        statusCode, response = self.apiCall(endpoint)
        if statusCode != 200: return
        
        return  {port['portId']: port for port in response}
    
    def getTrunkPorts(self) -> list[str]: return [str(key) for key, port in self.ports.items() if port['type'] == 'trunk']
    
    def changePortToAccess(self, portId: str) -> None: return self.updatePort(portId, {"type": "access"})
    
    def changePortToTrunk(self, portId: str) -> None: return self.updatePort(portId, {"type": "trunk"})
    
    def updatePortVlan(self, portId: str, newVlan: int) -> None: 
        for port in self.ports: 
            if port['type'] == 'trunk': return
        return self.updatePort(portId, {"vlan": newVlan})
    
    def getClients(self, trunkPorts: list[str] = []):
        endpoint = 'devices/%s/clients' % self.serial
        statusCode, response = self.apiCall(endpoint)
        
        if statusCode != 200: return
        
        return [client for client in response if client['switchport'] not in trunkPorts]
        
    def updatePort(self, portId: str, payload: dict):
        endpoint = 'devices/%s/switch/ports/%s' % (self.serial, portId)
        statusCode, response = self.apiCall(endpoint, payload, 'PUT')
        
        if statusCode != 200: return
        
        self.ports = self.getPorts()
        return 'Port %s updated' % portId