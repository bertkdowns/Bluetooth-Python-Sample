from openapi_client.models.solve_request import SolveRequest
from openapi_client.rest import ApiException
from openapi_client import ApiClient
import openapi_client
from pprint import pprint


class Flowsheet():
    def __init__(self, configuration,id):
        self.configuration = configuration
        self.id = id
        with ApiClient(configuration) as api_client:
            unitops_api = openapi_client.UnitopsApi(api_client)
            try:
                print("Getting Unit Ops")
                api_response = unitops_api.unitops_unitops_list(id)
                self.unitops = api_response
            except ApiException as e:
                print("Exception when calling UnitopsApi->unitops_unitops_list: %s\n" % e)
            try:
                print("Getting Material Streams")
                api_response = unitops_api.unitops_materialstreams_list(id)
                self.materialstreams = api_response
            except ApiException as e:
                print("Exception when calling UnitopsApi->unitops_materialstreams_list: %s\n" % e)
    
    def get_property_id(self,name,propkey):
        for unitop in self.unitops:
            if unitop.component_name == name:
                for property in unitop.properties.contained_properties:
                    if property.prop_key == propkey:
                        return property.id
        for materialstream in self.materialstreams:
            if materialstream.component_name == name:
                for property in materialstream.properties.contained_properties:
                    if property.prop_key == propkey:
                        return property.id
        return None
    
    def update_property(self,id,value):
        with ApiClient(self.configuration) as api_client:
            core_api = openapi_client.CoreApi(api_client)
            try:
                core_api.core_propertyinfo_partial_update(id, {
                    value:value
                })
            except ApiException as e:
                print("Exception when calling CoreApi->propertyinfo_partial_update: %s\n" % e)
    
    def solve(self):
        with ApiClient(self.configuration) as api_client:
            solve_api = openapi_client.SolveApi(api_client)
            solve_request = SolveRequest()
            solve_request.flowsheet_id = self.id
            try:
                api_response = solve_api.idaes_create(solve_request)
                pprint(api_response)
            except ApiException as e:
                print("Exception when calling SolveApi->solve: %s\n" % e)
            