from ..merakiObject import _MerakiObject
import json

class _PolicyObject(_MerakiObject):
    def __init__(self, apiKey: str, organizationId: str, id: str = None, 
                 name: str = None, category: str = None, type: str = None, 
                 address: str = None, groupIds: list[str] = None) -> None:
        
        super().__init__(apiKey)
        self.organizationId = organizationId
        self.id = id
        self.name = name
        self.category = category
        self.type = type
        self.address = address
        self.groupIds = groupIds
        
    def __repr__(self) -> str:
        return "Policy Object Name: %s, type: %s, address: %s" % (self.name, self.type, self.address)
    
    def get(self, poId):
        endpoint = 'organizations/%s/policyObjects/%s' % (self.organizationId, poId)
        statusCode, response = self.apiCall(endpoint)
        
        self.id = response['id']
        self.name = response['name']
        self.category = response['category']
        self.type = response['type']
        self.address = response[self.type]
        self.groupIds = response['groupIds']
        
    
    def create(self, name: str, type: str, addr: str, groupIds: list[str]):
        endpoint = 'organizations/%s/policyObjects' % self.organizationId
        payload = {
            "name": name.replace('.', '_').replace('*', ' W ').replace('/', '-'),
            "category": "network",
            "type": type,
            type: addr,
            "groupIds": groupIds
        }
        
        status_code, response = self.apiCall(endpoint, payload, 'POST')
        print(response)
        if status_code != 201: return
        
        self.id = response['id']
        self.name = name
        self.type = type
        self.address = addr
        self.groupIds = groupIds
        
    def delete(self):
        endpoint = 'organizations/%s/policyObjects/%s' % (self.organizationId, self.id)
        response = self._delete(endpoint)
        print(response.status_code)