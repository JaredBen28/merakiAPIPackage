from ..merakiObject import _MerakiObject
import json

class _PolicyObjectGroup(_MerakiObject):
    def __init__(self, apiKey: str, organizationId: str, id: str = None, 
                 name: str = None, objectIds: list[str] = None) -> None:
        super().__init__(apiKey)
        self.organizationId = organizationId
        self.id = id
        self.name = name
        self.objectIds = objectIds
    
    def __repr__(self) -> str:
        return "Policy object group Name: %s, id: %s" % (self.name, self.id)
    
    def get(self, policyObjectGroupId: str) -> None:
        endpoint = 'organizations/%s/policyObjects/groups/%s' % (self.organizationId, policyObjectGroupId)
        statusCode, response = self.apiCall(endpoint)
        
        if statusCode != 200: return None
        self.id = response['id']
        self.name = response['name']
        self.objectIds = response['objectIds']
    
    def create(self, name:str, policyObjectIds: list[str] = None) -> None:
        endpoint = 'organizations/%s/policyObjects/groups' % self.organizationId
        if len(name) > 38: 
            print('name to long')
            return None
        
        payload = {"name": name.replace('.', '_')}
        
        if policyObjectIds != None:
            payload = {
                "name": name.replace('.', '_'),
                "objectIds": policyObjectIds
                }
            
        _ , response = self.apiCall(endpoint, payload, 'POST')
        print(response)
        self.name = name
        self.id = response['id']
    
    def delete(self):
        endpoint = 'organizations/%s/policyObjects/groups/%s' % (self.organizationId, self.id)
        response = self._delete(endpoint)
        print(response.status_code)