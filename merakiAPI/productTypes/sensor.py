from ..device import Device
class _Sensor(Device):
    def __init__(self, apiKey, serial, payload: dict = None) -> None:
        super().__init__(apiKey, serial, True, payload = payload)
        
    def getMetrics(self) -> dict:
        endpoint = 'networks/%s/sensor/alerts/current/overview/byMetric' % self.networkId
        statusCode, response = self.apiCall(endpoint)
        
        return response