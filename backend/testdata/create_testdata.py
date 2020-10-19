import json
import requests
import pandas as pd
import random

def draw_representative_values(entities, k=100, pseudonym=False):
    df = pd.DataFrame(entities)
    if "_id" in df.columns:
        del df["_id"]
    new_df = pd.DataFrame(['test_entity_{}'.format(i) for i in range(k)])
    cols = [col for col in list(df.columns)]
    for col in cols:
        vals = (df[col].value_counts()/len(df[col]))
        if len(vals) == 0:
            properties = [0,1]
            weights = [0,1]
        else:
            properties = list(vals.index)
            weights = list(vals.values)
        
        new_df = pd.concat([new_df, pd.DataFrame(random.choices(properties, k=k, weights=weights))], axis=1)
    new_df.columns = ['_id'] + cols
    return new_df.to_dict(orient='records')


def flatten_json(nested_json):
    out = {}
    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name)
                i += 1
        else:
            out[name[:-1]] = x

    flatten(nested_json)
    return out


def cleaning_json_schema(pipe_id, json_entity_response):
    entities_to_remove = []
    for entity in json_entity_response[0]:
        if pipe_id not in entity and "_id" not in entity:
                entities_to_remove.append(entity)
    
    try:
        for mapping_entity in entities_to_remove:
            for entity in json_entity_response:
                for sesam_property in list(entity):
                    if mapping_entity == sesam_property:
                        entity.pop(sesam_property)
                    if pipe_id in sesam_property:
                        entity[sesam_property.split(":", 1)[1]] = entity.pop(sesam_property)
        
        for response_key, response_value in json_entity_response[0].items():
            if type(response_value) is dict:
                for nested_keys in list(response_value):
                    response_value[nested_keys.split(":", 1)[1]] = response_value.pop(nested_keys)
                    for keys, value in response_value.items():
                        if type(value) is list:
                            for nested_keys in value:
                                if type(nested_keys) is dict:
                                    try:
                                        response_value[nested_keys.split(":", 1)[-1]] = response_value.pop(nested_keys)
                                    except Exception:
                                        for keys in list(nested_keys):
                                            nested_keys[keys.split(":")[-1]] = nested_keys.pop(keys)
                                    for key, val in nested_keys.items():
                                        if type(val) is dict:
                                            for nested_val in list(val):
                                                val[nested_val.split(":")[-1]] = val.pop(nested_val)
                        
                        if type(value) is dict:
                            for keys_nested in list(value):
                                try:
                                    value[keys_nested.split(":", 1)[-1]] = value.pop(keys_nested)
                                except Exception:
                                    for keys in list(keys_nested):
                                            keys_nested[keys.split(":")[-1]] = keys_nested.pop(keys)

                                for nested_key, nested_value in value.items():
                                    if type(nested_value) is dict:
                                        for nested_keys in list(nested_value):
                                            nested_value[nested_keys.split(":")[-1]] = nested_value.pop(nested_keys)
                                              
            if type(response_value) is list:
                for nested_keys in response_value:
                    if type(nested_keys) is dict:
                        try:
                            response_value[nested_keys.split(":", 1)[-1]] = response_value.pop(nested_keys)
                        except Exception:
                            for keys in list(nested_keys):
                                nested_keys[keys.split(":")[-1]] = nested_keys.pop(keys)
                        for key, val in nested_keys.items():
                            if type(val) is dict:
                                for nested_val in list(val):
                                    val[nested_val.split(":")[-1]] = val.pop(nested_val)
                        
    except Exception as e:
        logger.error(f"Could not remove unnessary properties from this entity. Failed with : {e}")

    return json_entity_response


def create_embedded_testdata(input_pipe, counter, sesam_jwt, sesam_base_url):
    max_entities = 50
    header = {'Authorization': f'Bearer {sesam_jwt}', "content-type": "application/json"}
    pump_header = {'Authorization': f'Bearer {sesam_jwt}', "content-type": "application/x-www-form-urlencoded"}
    json_env = {'node-env': 'prod'}
    try:
        check_pipe_run = requests.post(f"{sesam_base_url}/pipes/{input_pipe}/pump", headers=pump_header, data=dict(operation="start"))
        if not check_pipe_run.ok:
            print(f"Unexpected error : {check_pipe_run.content}", 500)
            return print(f"Could not run your pipe with id : {input_pipe}. Skipping it.")

        if counter == 0:
            create_node_env = requests.post(f"{sesam_base_url}/env", headers=header, data=json.dumps(json_env), verify=False)
            if create_node_env.ok:
                print("created 'node-env' variable")

        sesam_config_request = requests.get(f"{sesam_base_url}/pipes/{input_pipe}/config", headers=header, verify=False)
        json_config_response = json.loads(sesam_config_request.content.decode('utf-8-sig'))
        sesam_entity_request = requests.get(f"{sesam_base_url}/datasets/{input_pipe}/entities?deleted=False&history=False", headers=header, verify=False)
        json_entity_response = json.loads(sesam_entity_request.content.decode('utf-8-sig'))
        json_schema_response = json.loads(sesam_entity_request.content.decode('utf-8-sig'))
       
        json_mapping_schema = cleaning_json_schema(input_pipe, json_schema_response[:1])

        flattened_entities = []
        for entity in json_entity_response:
            flattened_entities.append(flatten_json(entity))

        json_entity_response = draw_representative_values(flattened_entities,k=max_entities)

        embedded_entities = [] 
        for response_elements in json_entity_response:
            new_entity = {}
            for response_key, response_value in response_elements.items():
                for schema_elements in json_mapping_schema:
                    if response_key in schema_elements:
                        new_entity[response_key] = response_value
                        
                    if response_key.split(':', 1)[-1] in schema_elements:
                        new_entity[response_key.split(':', 1)[-1]] = response_value

                    if response_key not in schema_elements:
                        try:
                            for schema_key, schema_value in schema_elements.items():
                                if type(schema_value) is dict:
                                    for nested_key, nested_value in schema_value.items():
            
                                        if response_key.split(':')[-1] in nested_key:
                                            if schema_key not in new_entity:
                                                new_entity[schema_key] = {}
                                            new_entity[schema_key][nested_key] = response_value
                                        
                                        if type(nested_value) is list:
                                            if nested_key not in new_entity[schema_key]:
                                                new_entity[schema_key][nested_key] = []
                                                for nested_dicts in nested_value:
                                                    new_entity[schema_key][nested_key].append(nested_dicts)
                                        
                                        if type(nested_value) is dict:
                                            if response_key.split(':')[-1] in nested_key:
                                                if nested_key not in new_entity[schema_key]:
                                                    new_entity[schema_key][nested_key] = {}
                                                new_entity[schema_key][nested_key] = nested_value

                                        if nested_key not in new_entity[schema_key]:
                                            new_entity[schema_key][nested_key] = {}
                                        new_entity[schema_key][nested_key] = nested_value
      
                                if type(schema_value) is list:
                                    if schema_key not in new_entity:
                                        new_entity[schema_key] = []
                                        for nested_dicts in schema_value:
                                            new_entity[schema_key].append(nested_dicts)
                                            
                        except Exception:
                            pass      

            embedded_entities.append(new_entity)

        new_source = {
            "_id": json_config_response["_id"],
            "type": json_config_response["type"],
            "source": {
                "type": "conditional",
                "alternatives": {
                    "prod": json_config_response["source"],
                    "test": {
                        "type": "embedded",
                        "entities": embedded_entities
                    }
            },
            "condition": "$ENV(node-env)"
            },
            "transform": json_config_response["transform"]
            }
        
        check_response = requests.put(f"{sesam_base_url}/pipes/{input_pipe}/config?force=True", headers=header, data=json.dumps(new_source), verify=False)
        if not check_response.ok:
            return print(f"Unexpected error : {check_response.content}", 500)
        else:
            return print(f"Your pipe with id : {input_pipe} has been updated with test data")
    
    except Exception as e:
        return print(f"Your pipe with id : {input_pipe} could unfortunately not be updated... I failed with the following error : {e}")
