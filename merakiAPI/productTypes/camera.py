from ..device import Device

class _Camera(Device):
    def __init__(self, apiKey, serial, payload: dict = None) -> None:
        super().__init__(apiKey, serial, True, payload = payload)
    
    def getVideoLink(self) -> str:
        endpoint = 'devices/%s/camera/videoLink' % self.serial
        statusCode, response = self.apiCall(endpoint)
        if statusCode != 200: return
        
        self.url = response['url']
        print(self.url)
        return response['url']
    
    def getAnalyticsOverview(self) -> list[dict]:
        endpoint = 'devices/%s/camera/analytics/overview' % self.serial
        statusCode, response = self.apiCall(endpoint)
        
        if statusCode != 200: return
        return response