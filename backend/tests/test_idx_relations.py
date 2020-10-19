return_object = [('users', 'id'), ('posts', 'id'), ('age', 'id'),
                 ('comments', 'id')]

pipes_to_create = ['users', 'posts', 'comments', "random_table"]

index_relations_postgres = [[{'posts': 'id'}, {'users': 'id'}], [{'age': 'id'}, {'users': 'id'}], [{'comments': 'id'}, {'users': 'id'}], [{'users': 'id'}, {'posts': 'id'}], [{'users': 'id'}, {'posts': 'user_id'}], [{'age': 'id'}, {'posts': 'id'}], [{'age': 'id'}, {'posts': 'user_id'}], [{'comments': 'id'}, {'posts': 'id'}], [{'comments': 'id'}, {'posts': 'user_id'}], [{'users': 'id'}, {'age': 'id'}], [{'users': 'id'}, {'age': 'user_id'}], [{'users': 'id'}, {'age': 'age'}], [{'posts': 'id'}, {'age': 'id'}], [{'posts': 'id'}, {'age': 'user_id'}], [{'posts': 'id'}, {'age': 'age'}], [{'comments': 'id'}, {'age': 'id'}], [{'comments': 'id'}, {'age': 'user_id'}], [{'comments': 'id'}, {'age': 'age'}], [{'users': 'id'}, {'comments': 'id'}], [{'users': 'id'}, {'comments': 'user_id'}], [{'users': 'id'}, {'comments': 'post_id'}], [{'posts': 'id'}, {'comments': 'id'}], [{'posts': 'id'}, {'comments': 'user_id'}], [{'posts': 'id'}, {'comments': 'post_id'}], [{'age': 'id'}, {'comments': 'id'}], [{'age': 'id'}, {'comments': 'user_id'}], [{'age': 'id'}, {'comments': 'post_id'}]]
index_relations_mssql = [[{'accounts': 'id'}, {'contacts': 'id'}], [{'person': 'Customerid'}, {'contacts': 'id'}], [{'storedetails_enriched': 'SerialNumber'}, {'contacts': 'id'}], [{'contacts': 'id'}, {'accounts': 'id'}], [{'person': 'Customerid'}, {'accounts': 'id'}], [{'storedetails_enriched': 'SerialNumber'}, {'accounts': 'id'}], [{'accounts': 'id'}, {'person': 'Customerid'}], [{'contacts': 'id'}, {'person': 'Customerid'}], [{'storedetails_enriched': 'SerialNumber'}, {'person': 'Customerid'}], [{'accounts': 'id'}, {'storedetails_enriched': 'SerialNumber'}], [{'contacts': 'id'}, {'storedetails_enriched': 'SerialNumber'}], [{'person': 'Customerid'}, {'storedetails_enriched': 'SerialNumber'}]]

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

remaining_table_relations = []
for table in pipes_to_create:
    for fkey_table in index_relations_postgres:
        if table == list(fkey_table[0].keys())[0] and list(fkey_table[0].keys())[0] not in remaining_table_relations:
            remaining_table_relations.append(fkey_table)

#print(remaining_table_relations)

for ni_relation in remaining_table_relations:
    if list(ni_relation[0].keys())[0] in pipes_to_create:
        pipes_to_create.remove(list(ni_relation[0].keys())[0])

#print(pipes_to_create)


def create_pipe_with_idx_ni(connection_params, list_with_table_relations,
                        sesam_jwt, sesam_base_url):
    return_msg = None
    pipes = {}
    header = {
        'Authorization': f'Bearer {sesam_jwt}',
        "content_type": "application/json"
    }

    tmp_dict = {}
    for table in list_with_table_relations:
        pipe_id = list(table[0].keys())[0]
        pipe_id_column = list(table[0].values())[0]
        pipe_idx_table = list(table[1].keys())[0]
        pipe_idx_column = list(table[1].values())[0]
        
        if pipe_id in tmp_dict:
            tmp_dict[pipe_id].append([
                "add",
                f"{pipe_idx_table.replace('_', '-')}-{pipe_idx_column}-ni",
                [
                    "ni",
                    f"{connection_params['dbase']}-{pipe_idx_table.replace('_', '-')}",
                    f"_S.{pipe_id_column}"
                ]
            ])
        else:
            tmp_dict = {
                pipe_id : [[
                    "add",
                    f"{pipe_idx_table.replace('_', '-')}-{pipe_idx_column}-ni",
                    [
                        "ni",
                        f"{connection_params['dbase'].replace('_', '-')}-{pipe_idx_table.replace('_', '-')}",
                        f"_S.{pipe_id_column}"
                    ]
                ]]
            }

        pipe = {
            "_id":
            f"{connection_params['dbase']}-{pipe_id.replace('_', '-')}",
            "type": "pipe",
            "source": {
                "type": "sql",
                "system": f"{connection_params['dbName'].replace('_', '-')}",
                "table": f"{pipe_id}"
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
                                f"{connection_params['dbase']}-{pipe_id.replace('_', '-')}",
                                f"{pipe_id.replace('_', '-')}"
                            ]
                        ],
                    ] + tmp_dict[pipe_id]
                }
            }
        }

        pipes[pipe["_id"]] = pipe

    pipes = list(pipes.values())
    return print(pipes)


create_pipe_with_idx_ni(connection_params, remaining_table_relations, sesam_jwt, sesam_base_url)