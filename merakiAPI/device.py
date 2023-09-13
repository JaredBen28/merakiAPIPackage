from .merakiObject import _MerakiObject

############### Finished?? ###############

class Device(_MerakiObject):
    def __init__(self, apiKey: str, serial: str, claimed: bool = True, payload: dict = None) -> None:
        """ init device object

        Args:
            apiKey (str): api key
            serial (str): serial number of device
            claimed (bool, optional): if the device is claimed by network. Defaults to True.
            payload (dict, optional): payload if already have device settings. Defaults to None.
        """
        super().__init__(apiKey)
        
        self.serial = serial            
        if payload != None:
            self.__get(payload)
        if claimed:
            self.get()
    
    def __repr__(self):
        return "Serial: %s, Model: %s" % (self.serial, self.model)
    
    def __get(self, payload: dict) -> None:
        self.name = payload['name']
        self.model = payload['model']
        self.url = payload['url']
        self.networkId = payload['networkId']
        self.additionalOptions = {k: v for k, v in payload.items() if k not in ['name', 'model', 'url', 'networkId', 'serial']}
        
    def get(self) -> dict:
        """ gets the device info from the API

        Returns:
            dict: _description_
        """
        endpoint = 'devices/%s' % self.serial

        statusCode, response = self.apiCall(endpoint)
        
        if statusCode!= 200:
            print('Device Not Found')
            return
        self.name = response['name']
        self.model = response['model']
        self.url = response['url']
        self.networkId = response['networkId']
        self.additionalOptions = {k: v for k, v in response.items() if k not in ['name', 'model', 'url', 'networkId', 'serial']}
        
    def update(self, payload: dict):
        """ updates the device settings

        Args:
            payload (dict): payload based on the Merkai API documentation
        """
        endpoint = 'devices/%s' % self.serial

        statusCode, response = self.apiCall(endpoint, payload, 'PUT')
        
        if statusCode != 200:
            print('Update Failed')
            
        self.get()