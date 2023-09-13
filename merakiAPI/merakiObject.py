# import requests
from requests import request, exceptions

_verify = False
class _MerakiObject():
    def __init__(self, apiKey: str) -> None:
        """ _meraki object inti

        Args:
            apiKey (str): api key of user 
        """
        self._url = 'https://api.meraki.com/api/v1/%s' # endpoint of meraki api
        self._apiKey = apiKey
    
    def apiCall(self, endpoint: str, payload: dict = {}, method: str = 'GET'):
        """ send an api call to meraki api

        Args:
            endpoint (str): endpoint of the api
            payload (dict, optional): payload for the api call. Defaults to {}.
            method (str, optional): method to use 'POST' or 'PUT'. Defaults to 'GET'.

        Returns:
            _type_: _description_
        """
        headers = {
            'X-Cisco-Meraki-API-Key': self._apiKey,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # API call error correction
        try: # API call
            response = request(method, self._url % endpoint, headers=headers, json=payload, verify=_verify)
            response.raise_for_status()
        except exceptions.HTTPError as err: # Error handling
            if response.status_code == 400:
                print(err, response.json())
                print('Client error')
            elif response.status_code == 401:
                print(err, response.json())
                print(f'API Key {self._apiKey} is invalid. Please check your API key and try again.')
            elif response.status_code == 403:
                print(err, response.json())
                print('You do not have permission to perform this action.')
            elif response.status_code == 404:
                print(err, response.json())
                print('Resource does not exist')
            elif response.status_code == 429:
                print(err, response.json())
                print('You have exceeded your rate limit. Please wait and try again.')
            elif response.status_code >= 500:
                print(err, response.json())
                print('Meraki was unable to process your request.')
            else:
                print(err, response.json())
        
        return response.status_code, response.json()
    
    def _apiJsonErrorCall(self, endpoint, payload):
        headers = {
            'X-Cisco-Meraki-API-Key': self._apiKey,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = request('POST', self._url % endpoint, headers=headers, json=payload, verify=_verify)
        return response.status_code
        
    def _delete(self, endpoint: str) -> any:
        """ request delete endpoint

        Args:
            endpoint (str): endpoint of api

        Returns:
            any: response
        """
        headers = {'X-Cisco-Meraki-API-Key': self._apiKey}
        response = request('DELETE', self._url % endpoint, headers=headers, verify=_verify)
        return response
    
    def _changeOctet(cidr, octet, newValue) -> str:
        """ change an octet of cidr/ip

        Args:
            cidr (str): cidr to change
            octet (str): which octet to change
            newValue (str): new value for octet

        Returns:
            str: new cidr
        """
        c = cidr.split('.')
        if octet == 4:
            c3 = c[3].split('/')
            c3[0] = str(newValue)
            c[3] = '/'.join(c3)
        else:
            c[octet - 1] = str(newValue)
        return '.'.join(c)