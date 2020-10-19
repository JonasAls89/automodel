from flask import Flask, request, jsonify, Response
import json
import requests
import logging
import os
import sys
from datahubs.sesam import create_pipe, create_system, get_all_input_pipes, create_global, create_pipe_with_fkey_ni, create_pipe_with_idx_ni, get_all_pipes, get_global_pipe_config
from processing.mysql import connect_to_db as mysql_db
from processing.oracle import connect_to_db as oracle_db
from processing.postgres import connect_to_db as postgres_db
from processing.mssql import connect_to_db as mssql_db
from testdata.create_testdata import create_embedded_testdata
from flask_cors import CORS, cross_origin
from sesamutils import VariablesConfig
import urllib3

urllib3.disable_warnings()
app = Flask(__name__)
CORS(app,
     resources={r"/*": {
         "origins": "*"
     }},
     headers={
         'Access-Control-Request-Headers', 'Content-Type',
         'Access-Control-Allow-Origin'
     })

## Helpers
connecting_params = None
sesam_response = None
datahub_config_and_tables = None
fkey_relations = None
index_relations = None
logger = None


@app.route('/')
def index():
    output = {
        'service': 'Automodel up and running',
        'remote_addr': request.remote_addr
    }
    return jsonify(output)


## Get connection parameters for db connection and saving them to global variable "connecting_params"
@app.route('/connectors', methods=['POST'])
@cross_origin()
def get_connectors():
    global connecting_params
    connectors = request.json
    connecting_params = connectors
    return jsonify({"parameters": "committed"})


## Get all input pipes from SESAM to display in frontend for merging of globals.
@app.route('/get_pipes', methods=['POST'])
@cross_origin()
def get_pipes():
    return_object = []
    global datahub_config_and_tables
    global sesam_response
    connectors = request.json
    datahub_config_and_tables = connectors
    pipes_in_sesam = get_all_input_pipes(
        datahub_config_and_tables['sesamJWT'],
        datahub_config_and_tables['sesamBaseURL'])

    index_value = 1
    for pipe in pipes_in_sesam:
        return_object.append({"id": index_value, "name": pipe, "groupId": 1})
        index_value = index_value + 1

    sesam_response = {"result": return_object}
    return {"pipes": pipes_in_sesam}

    
## Get all pipes from SESAM to display in frontend.
@app.route('/get_all_pipes', methods=['POST'])
@cross_origin()
def scan_sesam():
    return_object = []
    global datahub_config_and_tables
    global sesam_response
    connectors = request.json
    datahub_config_and_tables = connectors
    pipes_in_sesam = get_all_pipes(
        datahub_config_and_tables['sesamJWT'],
        datahub_config_and_tables['sesamBaseURL'])

    for pipe in pipes_in_sesam:
        return_object.append(pipe)
    
    return_object = sorted(return_object, key=str.swapcase)

    if len(return_object) == 0:
        tmp_pipes_for_frontend = ["It seems you have not started using SESAM yet.", "Lets run a scan of your database to get started!"]
        for pipe in tmp_pipes_for_frontend:
            return_object.append(pipe)

    sesam_response = {"result": return_object}
    return {"pipes": pipes_in_sesam}


## Get all input pipes from SESAM to display in frontend for merging of globals.
@app.route('/create_global_list', methods=['POST'])
@cross_origin()
def global_list():
    return_object = []
    response_object = None
    global sesam_response
    connectors = request.json
    pipes_to_use_for_globals = connectors['pipes']

    global_groups = [
        {
          'id': 1,
          'name': "Default List",
          'items': [],
        },
        {
          'id': 2,
          'name': "First Global",
          'items': [],
        },
        {
          'id': 3,
          'name': "Second Global",
          'items': [],
        },
        {
          'id': 4,
          'name': "Third Global",
          'items': [],
        },
        {
          'id': 5,
          'name': "Fourth Global",
          'items': [],
        },
        {
          'id': 6,
          'name': "Fifth Global",
          'items': [],
        }
    ]

    index_value = 1
    group_count = 2
    element_count = 1
    tmp_globals = []
    tmp_pipes_in_globals = []
    for pipe in pipes_to_use_for_globals:
        if "global" in pipe and pipe not in tmp_globals:
            tmp_globals.append(pipe)
            pipes_in_global = get_global_pipe_config(pipe, datahub_config_and_tables['sesamJWT'],
                      datahub_config_and_tables['sesamBaseURL'])
            tmp_pipes_in_globals.extend(pipes_in_global)
            if global_groups[element_count].get('id') == group_count:
                global_groups[element_count]['name'] = pipe
                for tmp_pipe in tmp_pipes_in_globals:
                    global_groups[element_count]['items'].append({"id": index_value, "name": tmp_pipe, "groupId": group_count})
                    index_value = index_value + 1
                element_count = element_count + 1
                group_count = group_count + 1

        else:
            if type(pipe) is dict:
                return_object.append(pipe)
            else:
                return_object.append({"id": index_value, "name": pipe, "groupId": 1})
                index_value = index_value + 1
        
        tmp_pipes_in_globals = []

    global_groups[0]['items'].extend(return_object)
    response_object = global_groups
    
    tmp_globals = []

    sesam_response = {"result": response_object}
    return {"pipes": pipes_to_use_for_globals}


## Creating globals from excisting SESAM integration
@app.route('/create_globals', methods=['POST'])
@cross_origin()
def get_globals():
    sesam_global_response = None
    global datahub_config_and_tables
    global sesam_response
    connectors = request.json
    global_selection = connectors

    selected_globals = []
    for element in global_selection['globalGroups']:
        for key, value in element.items():
            if key == "name":
                if value == "Default List" or value == "First Global" or value == "Second Global" or value == "Third Global" or value == "Fourth Global" or value == "Fifth Global":
                    pass
                else:
                    selected_globals.append(element)

    global_name = None
    pipe_names = []
    index = 1
    for element in selected_globals:
        global_name = element['name']
        for pipe in element['items']:
            pipe_names.append(f"{pipe['name']} pip{index}")
            index = index + 1
        create_global(global_name, pipe_names,
                      datahub_config_and_tables['sesamJWT'],
                      datahub_config_and_tables['sesamBaseURL'])
        pipe_names = []
        index = 1

    sesam_response = {
        "sesam_result": "Your global pipes have been created! ;)"
    }
    return {"system_result": sesam_global_response}


## Create embedded test data in SESAM.
@app.route('/create_testdata', methods=['POST'])
@cross_origin()
def testdata():
    sesam_pipe_response = None
    global datahub_config_and_tables
    global sesam_response
    connectors = request.json
    pipes = connectors['pipes']
    counter = 0

    for pipe in pipes:
        create_embedded_testdata(pipe, counter, datahub_config_and_tables['sesamJWT'],
            datahub_config_and_tables['sesamBaseURL'])
        counter = counter + 1

    sesam_response = {
        "sesam_result": "Your pipes have been embedded with test data! ;)"
    }
    return {"response": 'job done..'}


## Create dataflow excluding globals and check for fkey_relations or index_relations.
@app.route('/create_dataflow_no_globals', methods=['POST'])
@cross_origin()
def create_dataflow():
    sesam_system_response = None
    sesam_pipe_response = None
    global datahub_config_and_tables
    global sesam_response
    global fkey_relations
    global index_relations
    connectors = request.json
    pipes = connectors['tables']
    test_data_choice = connectors['testDataChoice']

    #creating system
    sesam_system_response = create_system(
        connecting_params, datahub_config_and_tables['sesamJWT'],
        datahub_config_and_tables['sesamBaseURL'])
    if sesam_system_response != "Your system has been created":
        sesam_system_response = "Your system could not be created. Make sure your provided SESAM variables are correct"

    #creating pipes with or without relations
    pipes_to_create = []
    for pipe in pipes:
        pipes_to_create.append(pipe['name'])

    remaining_table_relations = []
    if fkey_relations != []:
        for table in pipes_to_create:
            for fkey_table in fkey_relations:
                if table == fkey_table[0]:
                    remaining_table_relations.append(fkey_table)

        for ni_relation in remaining_table_relations:
            if ni_relation[0] in pipes_to_create:
                pipes_to_create.remove(ni_relation[0])

        create_pipe_with_fkey_ni(connecting_params, remaining_table_relations,
                            datahub_config_and_tables['sesamJWT'],
                            datahub_config_and_tables['sesamBaseURL'])

        # remaining tables without ni's
        sesam_pipe_response = create_pipe(
            connecting_params, pipes_to_create,
            datahub_config_and_tables['sesamJWT'],
            datahub_config_and_tables['sesamBaseURL'])
        if sesam_pipe_response != "Pipes created":
            sesam_pipe_response = "Your pipes could not be created. Make sure your provided SESAM variables are correct"

    if index_relations != []:
        for table in pipes_to_create:
            for fkey_table in index_relations:
                if table == list(fkey_table[0].keys())[0] and list(fkey_table[0].keys())[0] not in remaining_table_relations:
                    remaining_table_relations.append(fkey_table)

        for ni_relation in remaining_table_relations:
            if list(ni_relation[0].keys())[0] in pipes_to_create:
                pipes_to_create.remove(list(ni_relation[0].keys())[0])

        create_pipe_with_idx_ni(connecting_params, remaining_table_relations,
                            datahub_config_and_tables['sesamJWT'],
                            datahub_config_and_tables['sesamBaseURL'])

        # remaining tables without ni's
        sesam_pipe_response = create_pipe(
            connecting_params, pipes_to_create,
            datahub_config_and_tables['sesamJWT'],
            datahub_config_and_tables['sesamBaseURL'])
        if sesam_pipe_response != "Pipes created":
            sesam_pipe_response = "Your pipes could not be created. Make sure your provided SESAM variables are correct"

    if index_relations == [] and fkey_relations == []:
        sesam_pipe_response = create_pipe(
            connecting_params, pipes_to_create,
            datahub_config_and_tables['sesamJWT'],
            datahub_config_and_tables['sesamBaseURL'])
        if sesam_pipe_response != "Pipes created":
            sesam_pipe_response = "Your pipes could not be created. Make sure your provided SESAM variables are correct"

    if test_data_choice == "Create embedded test data":
        counter = 0
        if len(pipes_to_create) != 0:
            for pipe in pipes_to_create:
                pipe_id = f"{connecting_params['dbase']}-{pipe.replace('_', '-')}"
                create_embedded_testdata(pipe_id, counter, datahub_config_and_tables['sesamJWT'],
            datahub_config_and_tables['sesamBaseURL'])
                counter = counter + 1
        
        if len(remaining_table_relations) != 0:
            pipes_with_test_data = []
            for pipe in remaining_table_relations:
                pipe_id = None
                if index_relations != []:
                    tmp_pipe_id = list(pipe[0].keys())[0]
                    pipe_id = f"{connecting_params['dbase']}-{tmp_pipe_id.replace('_', '-')}"
                    if pipe_id not in pipes_with_test_data:
                        pipes_with_test_data.append(pipe_id)
                    else:
                        continue

                if fkey_relations != []:
                    pipe_id = f"{connecting_params['dbase']}-{pipe[0].replace('_', '-')}"
                    if pipe_id not in pipes_with_test_data:
                        pipes_with_test_data.append(pipe_id)
                    else:
                        continue
                
                create_embedded_testdata(pipe_id, counter, datahub_config_and_tables['sesamJWT'],
            datahub_config_and_tables['sesamBaseURL'])
                
                counter = counter + 1

    sesam_response = {
        "sesam_result": "Your system and pipes have been created! ;)"
    }
    return {
        "system_result": sesam_system_response,
        "pipe_result": sesam_pipe_response
    }


## Create dataflow including globals and check for fkey_relations or index_relations.
@app.route('/create_dataflow_with_globals', methods=['POST'])
@cross_origin()
def create_dataflow_globals():
    sesam_system_response = None
    sesam_pipe_response = None
    sesam_global_response = None
    global datahub_config_and_tables
    global sesam_response
    global fkey_relations
    global index_relations
    connectors = request.json
    test_data_choice = connectors['testDataChoice']

    sesam_system_response = create_system(
        connecting_params, datahub_config_and_tables['sesamJWT'],
        datahub_config_and_tables['sesamBaseURL'])
    if sesam_system_response != "Your system has been created":
        sesam_system_response = "Your system could not be created. Make sure your provided SESAM variables are correct"

    selected_globals = []
    for element in connectors['globalGroups']:
        for key, value in element.items():
            if key == "name":
                if value == "Default List" or value == "First Global" or value == "Second Global" or value == "Third Global" or value == "Fourth Global" or value == "Fifth Global":
                    pass
                else:
                    selected_globals.append(element)

    pipes_to_create = []
    for element in connectors['globalGroups']:
        for key, value in element.items():
            if value == "Default List":
                for dict_element in element['items']: 
                    pipes_to_create.append(dict_element['name'])

    global_name = None
    pipe_names = []
    
    index = 1
    for element in selected_globals:
        global_name = element['name']
        for pipe in element['items']:
            pipes_to_create.append(pipe['name'].replace('_', '-'))
            pipe_names.append(
                f"{connecting_params['dbase']}-{pipe['name'].replace('_', '-')} pip{index}"
            )
            index = index + 1

        sesam_global_response = create_global(
            global_name, pipe_names, datahub_config_and_tables['sesamJWT'],
            datahub_config_and_tables['sesamBaseURL'])
        if sesam_global_response != "Global created":
            sesam_global_response = "All of your globals could not be created. Check in Sesam to see what has been created"

        pipe_names = []
        index = 1

    remaining_table_relations = []
    if fkey_relations != []:
        for table in pipes_to_create:
            for fkey_table in fkey_relations:
                if table == fkey_table[0]:
                    remaining_table_relations.append(fkey_table)

        for ni_relation in remaining_table_relations:
            if ni_relation[0] in pipes_to_create:
                pipes_to_create.remove(ni_relation[0])

        create_pipe_with_fkey_ni(connecting_params, remaining_table_relations,
                            datahub_config_and_tables['sesamJWT'],
                            datahub_config_and_tables['sesamBaseURL'])

        # remaining tables without ni's
        sesam_pipe_response = create_pipe(
            connecting_params, pipes_to_create,
            datahub_config_and_tables['sesamJWT'],
            datahub_config_and_tables['sesamBaseURL'])
        if sesam_pipe_response != "Pipes created":
            sesam_pipe_response = "Your pipes could not be created. Make sure your provided SESAM variables are correct"

    if index_relations != []:
        for table in pipes_to_create:
            for fkey_table in index_relations:
                if table == list(fkey_table[0].keys())[0] and list(fkey_table[0].keys())[0] not in remaining_table_relations:
                    remaining_table_relations.append(fkey_table)

        for ni_relation in remaining_table_relations:
            if list(ni_relation[0].keys())[0] in pipes_to_create:
                pipes_to_create.remove(list(ni_relation[0].keys())[0])

        create_pipe_with_idx_ni(connecting_params, remaining_table_relations,
                            datahub_config_and_tables['sesamJWT'],
                            datahub_config_and_tables['sesamBaseURL'])

        # remaining tables without ni's
        sesam_pipe_response = create_pipe(
            connecting_params, pipes_to_create,
            datahub_config_and_tables['sesamJWT'],
            datahub_config_and_tables['sesamBaseURL'])
        if sesam_pipe_response != "Pipes created":
            sesam_pipe_response = "Your pipes could not be created. Make sure your provided SESAM variables are correct"

    if index_relations == [] and fkey_relations == []:
        sesam_pipe_response = create_pipe(
            connecting_params, pipes_to_create,
            datahub_config_and_tables['sesamJWT'],
            datahub_config_and_tables['sesamBaseURL'])
        if sesam_pipe_response != "Pipes created":
            sesam_pipe_response = "Your pipes could not be created. Make sure your provided SESAM variables are correct"

    if test_data_choice == "Create embedded test data":
        counter = 0
        if len(pipes_to_create) != 0:
            for pipe in pipes_to_create:
                pipe_id = f"{connecting_params['dbase']}-{pipe.replace('_', '-')}"
                create_embedded_testdata(pipe_id, counter, datahub_config_and_tables['sesamJWT'],
            datahub_config_and_tables['sesamBaseURL'])
                counter = counter + 1
        if len(remaining_table_relations) != 0:
            pipes_with_test_data = []
            for pipe in remaining_table_relations:
                pipe_id = None
                if index_relations != []:
                    tmp_pipe_id = list(pipe[0].keys())[0]
                    pipe_id = f"{connecting_params['dbase']}-{tmp_pipe_id.replace('_', '-')}"
                    if pipe_id not in pipes_with_test_data:
                        pipes_with_test_data.append(pipe_id)
                    else:
                        continue

                if fkey_relations != []:
                    pipe_id = f"{connecting_params['dbase']}-{pipe[0].replace('_', '-')}"
                    if pipe_id not in pipes_with_test_data:
                        pipes_with_test_data.append(pipe_id)
                    else:
                        continue
                
                create_embedded_testdata(pipe_id, counter, datahub_config_and_tables['sesamJWT'],
            datahub_config_and_tables['sesamBaseURL'])
                
                counter = counter + 1
    
    sesam_response = {
        "sesam_result": "Your system and pipes have been created! ;)"
    }

    return {
        "system_result": sesam_system_response,
        "pipe_result": sesam_pipe_response,
        "global_result": sesam_global_response
    }


## Get initial scan of db, get relations and write to globals [fkey_relations, index_relations]
@app.route('/scan_db', methods=['GET'])
@cross_origin()
def get_db_data():
    global connecting_params
    global fkey_relations
    global index_relations
    fkey_query_relations = None
    index_query_relations = None
    tables = []
    pkeys = []
    option = connecting_params['option']
    connecting_params["dbase"] = connecting_params["dbase"].lower()

    if option[0] == "Foreign Key references" or option == "Foreign Key references":
        option = "Fkey"
    if option[0] == "Index references" or option == "Index references":
        option = "Index"
    
    if connecting_params["dbase"] == "mysql":
        table_result, fkey_query_relations, index_query_relations = mysql_db(
            connecting_params, option)
    if connecting_params["dbase"] == "postgresql":
        table_result, fkey_query_relations, index_query_relations = postgres_db(
            connecting_params, option)
    if connecting_params["dbase"] == "oracle":
        table_result, fkey_query_relations, index_query_relations = oracle_db(
            connecting_params, option)
    if connecting_params["dbase"] == "mssql":
        table_result, fkey_query_relations, index_query_relations = mssql_db(
            connecting_params, option)

    fkey_relations = fkey_query_relations
    index_relations = index_query_relations

    index_value = 1
    for table, pkey in table_result:
        tables.append({"id": index_value, "name": table, "groupId": 1})
        pkeys.append(pkey)
        index_value = index_value + 1

    return {"result": tables}


## General response...
@app.route('/sesam_response', methods=['GET'])
def sesam_result():
    global sesam_response
    return sesam_response


if __name__ == '__main__':
    # Set up logging
    format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logger = logging.getLogger('Automodel is listening!..')

    # Log to stdout
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(stdout_handler)

    logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)