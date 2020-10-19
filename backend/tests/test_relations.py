import requests
import logging
import json
from ast import literal_eval

connection_params = {
    'dbase': 'postgresql',
    'dbHost': 'localhost',
    'dbPort': '5432',
    'dbName': 'postgres',
    'dbUser': 'postgres',
    'dbPassword': 'Testing Denmark',
    'option': ['No references']
}
sesam_jwt = "test2"
sesam_base_url = "test4"

picked_tables = ['users', 'posts', 'comments', "random_table"]
fkey_relations = [('posts', 'user_id', 'users', 'id'),
                  ('age', 'user_id', 'users', 'id'),
                  ('comments', 'user_id', 'users', 'id'),
                  ('comments', 'post_id', 'posts', 'id')]

remaining_table_relations = []
for table in picked_tables:
    #print(table)
    for fkey_table in fkey_relations:
        if table == fkey_table[0]:
            remaining_table_relations.append(fkey_table)
            #print(fkey_table[0])

for ni_relation in remaining_table_relations:
    if ni_relation[0] in picked_tables:
        picked_tables.remove(ni_relation[0])

## picked_tables will be send to old function.

##remaining_table_relations need to be send to below func


def create_pipe_with_ni(connection_params, list_with_table_relations,
                        sesam_jwt, sesam_base_url):
    return_msg = None
    pipes = {}
    header = {
        'Authorization': f'Bearer {sesam_jwt}',
        "content_type": "application/json"
    }

    tmp_dict = {}
    for table in list_with_table_relations:
        if table[0] in tmp_dict:
            tmp_dict[table[0]].append([
                "add",
                f"{connection_params['dbName']}-{table[2].replace('_', '-')}-{table[3]}-ni",
                [
                    "ni",
                    f"{connection_params['dbase'].replace('_', '-')}-{connection_params['dbName']}-{table[2].replace('_', '-')}",
                    f"_S.{table[1]}"
                ]
            ])
        else:
            tmp_dict = {
                table[0]: [[
                    "add",
                    f"{connection_params['dbName']}-{table[2].replace('_', '-')}-{table[3]}-ni",
                    [
                        "ni",
                        f"{connection_params['dbase'].replace('_', '-')}-{connection_params['dbName']}-{table[2].replace('_', '-')}",
                        f"_S.{table[1]}"
                    ]
                ]]
            }

        pipe = {
            "_id":
            f"{connection_params['dbase']}-{table[0].replace('_', '-')}",
            "type": "pipe",
            "source": {
                "type": "sql",
                "system": f"{connection_params['dbName'].replace('_', '-')}",
                "table": f"{table[0]}"
            },
            "transform": {
                "type": "dtl",
                "rules": {
                    "default": [
                        ["copy", "*"],
                        [
                            "add", "rdf:type",
                            [
                                "ni",
                                f"{connection_params['dbase']}-{table[0].replace('_', '-')}",
                                f"{table[0].replace('_', '-')}"
                            ]
                        ],
                    ] + tmp_dict[table[0]]
                }
            }
        }

        pipes[pipe["_id"]] = pipe

    pipes = list(pipes.values())
    for pipe in pipes:
        print(pipe)

    return pipes


create_pipe_with_ni(connection_params, remaining_table_relations, sesam_jwt,
                    sesam_base_url)


def test_func():
    for table in list_with_table_relations:
        pipe = {
            "_id": f"{connection_params['dbase']}-{table.replace('_', '-')}",
            "type": "pipe",
            "source": {
                "type": "sql",
                "system": f"{connection_params['dbName'].replace('_', '-')}",
                "table": f"{table[0]}"
            },
            "transform": {
                "type": "dtl",
                "rules": {
                    "default":
                    [["copy", "*"],
                     [
                         "add", "rdf:type",
                         [
                             "ni",
                             f"{connection_params['dbase']}-{table[0].replace('_', '-')}",
                             f"{table[0].replace('_', '-')}"
                         ]
                     ]]
                }
            }
        }
        pipes.append(pipe)

    for pipe in pipes:
        sesam_response = requests.post(f"{sesam_base_url}/pipes",
                                       headers=header,
                                       data=json.dumps([pipe]),
                                       verify=False)
        if not sesam_response.ok:
            print(sesam_response.content)
        else:
            print(f"Pipe '{pipe['_id']}' has been created")
            return_msg = "Pipes created"

    return msg