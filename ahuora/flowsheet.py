from openapi.openapi_client.models.solve_request import SolveRequest
from openapi.openapi_client.rest import ApiException
from openapi.openapi_client import ApiClient
from pprint import pprint


class Flowsheet():
    def __init__(self, configuration,id):
        self.configuration = configuration
        with ApiClient(configuration) as api_client:
            unitops_api = api_client.UnitopsApi()
            try:
                api_response = unitops_api.unitops_unitops_list(id)
                self.unitops = api_response.unitops
            except ApiException as e:
                print("Exception when calling UnitopsApi->unitops_unitops_list: %s\n" % e)
            try:
                api_response = unitops_api.unitops_materialstreams_list(id)
                self.materialstreams = api_response
            except ApiException as e:
                print("Exception when calling UnitopsApi->unitops_materialstreams_list: %s\n" % e)