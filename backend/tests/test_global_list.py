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

group_count = 2
element_count = 1

if global_groups[element_count].get('id') == group_count:
    print(global_groups[element_count]['name'])
    print(global_groups[element_count]['items'])