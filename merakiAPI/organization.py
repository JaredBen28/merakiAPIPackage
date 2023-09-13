from typing import Union
from .merakiObject import _MerakiObject
from .organizationObjects import _PolicyObject, _PolicyObjectGroup
from .productTypes import _Switch
############### Tested ###############
 
class Organization(_MerakiObject): 
    def __init__(self, apiKey: str, name: str) -> None: 
        """ init organization object

        Args:
            apiKey (str): api key of user
            name (str): name of organization (alphanumeric, space, dash, or underscore characters only)
        """
        
        super().__init__(apiKey)
        
        self.name = name
        self.id = self.__getId()
        
        if self.id == None: return
        
        self.policyObjects = self.__getPolicyObjects()
        self.policyObjectGroups = self.__getPolicyObjectGroups()
    
    def __repr__(self) -> str: 
        return "organization name: %s, organization id: %s" % (self.name, self.id)
    
    def __getId(self): 
        statusCode, response = self.apiCall('organizations', self._apiKey)
        if statusCode != 200: return None
        
        for org in response:
            if self.name == org['name']:
                return org['id']

    def getAllNetworkIds(self): 
        """ get networks associated with organization
        """
        endpoint = 'organizations/%s/networks' % self.id
        statusCode, response = self.apiCall(endpoint, self._apiKey)
        return [network['id'] for network in response]
    
    def __getPolicyObjects(self) -> list: 
        endpoint = 'organizations/%s/policyObjects' % self.id
        statusCode, response = self.apiCall(endpoint)
        if statusCode != 200: return
        
        return [_PolicyObject(self._apiKey, self.id, po['id'], 
                              po['name'], po['category'], po['type'], po[po['type']], po['groupIds']) 
                for po in response]
        
    def getPolicyObject(self, id: str = None, name: str = None): 
        """ gets a policy object object from object id or name

        Args:
            id (str, optional): id of policy object. Defaults to None.
            name (str, optional): name of policy object. Defaults to None. (alphanumeric, space, dash, or underscore characters only)

        Returns:
            policy object object or None
        """
        
        if id  == None and name == None: return
        
        for _PO in self.policyObjects:
            if id == _PO.id or name == _PO.name:
                return _PO
       
    
    def createPolicyObject(self, name: str, type: str, addr: str, groupIds: list[str] = None) -> _PolicyObject: 
        """ creates a new policy object object within organization object

        Args:
            name (str): name of policy object (alphanumeric, space, dash, or underscore characters only)
            type (str): type of policy object ['cidr', 'fqdn']
            addr (str): cidr or fqdn of policy object
            groupIds (list[str]): a list of the groupIds the policy object is a part of

        Returns:
            policy object object or None
        """
        name = name.replace('!', '').replace('@', '').replace('#', '').replace('$', '').replace('%', '').replace('^', '').replace('&', '').replace('*', '').replace('(', '').replace(')', '').replace('+', '').replace('=', '').replace('{', '').replace('}', '').replace('[', '').replace(']', '').replace('|', '').replace('\\', '').replace(':', '').replace(';', '').replace('"', '').replace('\'', '').replace('<', '').replace('>', '').replace(',', '').replace('.', '').replace('?', '').replace('/', '').replace('~', '').replace('`', '')
        _PO = _PolicyObject(self._apiKey, self.id)
        self.policyObjects.append(_PO.create(name, type, addr, groupIds))
        return _PO
    
    def createWildCardMask(self, name: str, ip: str) -> None: 
        """ create a wildcard mask of policy object spread over two policy object groups

        Args:
            name (str): name of policy object (alphanumeric, space, dash, or underscore characters only)
            addr (str): ip address of policy object wildcard with wildcard as '*' ex: 10.10.*.0
        """
        
        self.createPolicyObjectRange(name, ip, 0, 255)
    
    def createPolicyObjectRange(self, name: str, ip: str, startingValue: int, endingValue: int, policyObjectGroups: list[str] = None) -> None: 
        """ creates a policy object range from a start to ending value

        Args:
            name (str): name of policy object (alphanumeric, space, dash, or underscore characters only)
            ip (str): ip address of policy object changing value as '*' ex: 10.10.*.10/24 (will not work for last octet)
            startingValue (int): starting value of the range
            endingValue (int): ending value of the range (inclusive)
            policyObjectGroups (list[str], optional): list of policy object group ids to add policy object to, if none make new group. Defaults to None.
        """
        name = name.replace('!', '').replace('@', '').replace('#', '').replace('$', '').replace('%', '').replace('^', '').replace('&', '').replace('*', '').replace('(', '').replace(')', '').replace('+', '').replace('=', '').replace('{', '').replace('}', '').replace('[', '').replace(']', '').replace('|', '').replace('\\', '').replace(':', '').replace(';', '').replace('"', '').replace('\'', '').replace('<', '').replace('>', '').replace(',', '').replace('.', '').replace('?', '').replace('/', '').replace('~', '').replace('`', '')
        if not '.*.' in ip: return
        
        if endingValue - startingValue <= 128:
            if policyObjectGroups == None: 
                POG = self.createPolicyObjectGroup('%s %s-%s' % (name, startingValue, endingValue))
                POG = POG.id
            else:
                POG = policyObjectGroups
            for value in range(startingValue, endingValue + 1):
                self.createPolicyObject('%s wildcard-%i' % (name, value), 'cidr', ip.replace('*', str(value)), [POG])
        else:
            if policyObjectGroups == None:
                POG1 = self.createPolicyObjectGroup('%s %s-127' % (name, startingValue))
                POG1 = POG1.id
                POG2 = self.createPolicyObjectGroup('%s 128-%s' % (name, endingValue))
                POG2 = POG2.id
            else:
                POG1 = POG2 = policyObjectGroups
            for value in range(startingValue, 128):
                self.createPolicyObject('%s wildcard-%i' % (name, value), 'cidr', ip.replace('*', str(value)), [POG1])
            for value in range(128, endingValue + 1):
                self.createPolicyObject('%s wildcard-%i' % (name, value), 'cidr', ip.replace('*', str(value)), [POG2])
    
    def deletePolicyObject(self, name: str) -> str: 
        """ delete policy object by name

        Args:
            name (str): name of policy object to delete

        Returns:
            str: id of deleted policy object
        """
        for po in self.policyObjects:
            if po.name == name:
                po.delete()
                self.policyObjects.remove(po)
                return po.id
            
    def __getPolicyObjectGroups(self) -> list: 
        endpoint = 'organizations/%s/policyObjects/groups' % self.id
        statusCode, response = self.apiCall(endpoint)
        
        if statusCode != 200: return
        
        POG = []
        for pog in response:
            _POG = _PolicyObjectGroup(self._apiKey, self.id, 
                                      pog['id'], pog['name'], pog['objectIds'])
            POG.append(_POG)
            
        return POG
        
    def getPolicyObjectGroup(self, id: str = None, name: str = None) -> str: 
        """ gets a policy object group object from object id or name

        Args:
            id (str, optional): id of policy object. Defaults to None.
            name (str, optional): name of policy object. Defaults to None. (alphanumeric, space, dash, or underscore characters only)

        Returns:
            policy object group object or None
        """
        if id  == None and name == None: return
        
        for _POG in self.policyObjectGroups:
            if id == _POG.id or name == _POG.name:
                return _POG
        
    def createPolicyObjectGroup(self, name: str, policyObjectIds: list[str] = None): 
        """ create Policy Object Group for organization object

        Args:
            name (str): name of policy object group (alphanumeric, space, dash, or underscore characters only)
            policyObjectIds (list[str], optional): list of policy object ids to add to new group. Defaults to None.

        Returns:
            policy object group object
        """
        name = name.replace('!', '').replace('@', '').replace('#', '').replace('$', '').replace('%', '').replace('^', '').replace('&', '').replace('*', '').replace('(', '').replace(')', '').replace('+', '').replace('=', '').replace('{', '').replace('}', '').replace('[', '').replace(']', '').replace('|', '').replace('\\', '').replace(':', '').replace(';', '').replace('"', '').replace('\'', '').replace('<', '').replace('>', '').replace(',', '').replace('.', '').replace('?', '').replace('/', '').replace('~', '').replace('`', '')
        _POG = _PolicyObjectGroup(self._apiKey, self.id)
        self.policyObjectGroups.append(_POG.create(name))
        return _POG

    def deletePolicyObjectGroup(self, name: str) -> str: 
        """ deletes policy object group from organization 

        Args:
            name (str): name of policy object group

        Returns:
            str: policy object group id
        """
        for pog in self.policyObjectGroups:
            if pog.name == name:
                pog.delete()
                self.policyObjectGroups.remove(pog)
                return pog.id
            
    def deletePolicyObjectGroupAndObjects(self, name:str) -> list[str]: 
        """ deletes a group and all policy objects in that group

        Args:
            name (str): name of the group to delete

        Returns:
            list[str]: ids of all policy objects deleted
        """
        pog = self.deletePolicyObjectGroup(name)
        removed = []
        while True:            
            removedLen = len(removed)
            for po in self.policyObjects:
                if pog in po.groupIds:
                    po.delete()
                    self.policyObjects.remove(po)
                    removed.append(po.id)
            
            if removedLen == len(removed): break
        return removed
        
    def getOrganizationSwitches(self, withTrunks: bool = False): 
        """ returns a list of all switches in organization

        Args:
            withTrunks (bool): changes response to a list of switches and their trunk ports

        Returns:
            list: Either a list of switches or a list of switches and their trunk ports
        """
        switches = [_Switch(self._apiKey, device['serial']) for device in self.getOrganizationDevices() if 'MS' in device['model']]
        if not withTrunks:
            return switches
        else:
            return [[switch, switch.getTrunkPorts()] for switch in switches]
    
    def getOrganizationDevices(self) -> list[dict]:
        """ returns a list of all devices in organization (for testing only)

        Returns:
            list[dict]: list of all devices in organization
        """
        endpoint = 'organizations/%s/devices' % self.id
        statusCode, response = self.apiCall(endpoint)
        
        if statusCode != 200: return
        
        return response 