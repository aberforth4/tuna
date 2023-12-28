Tuna is a tool that can help you test [OpenFGA](https://openfga.dev/) authorization models. Such models describe how various objects should relate to each other, but where to get objects themselves? 
It's Tuna's turn; it takes a DSL authorization model and generates users and objects to fill your model. 
You can load them into an OpenFGA instance and perform various tests, such as stress tests, to be sure that your authorization model and OpenFGA instance deployment fit your needs.
```
usage: python tuna.py [-h] --mod MOD [--root_num ROOT_NUM] [--node_num NODE_NUM] [--leaf_num LEAF_NUM] [--user_num USER_NUM]
               [--make_pub_obj] [--make_wrong_tuples] [--user_type USER_TYPE]

Tuna - tool that can generate for you tuples to test your OpenFGA authorization model in DSL form.

options:
  -h, --help            show this help message and exit
  --mod MOD             --mod=PATH_2_MODEL_FILE Always required. Path to file with your OpenFGA authorization model in
                        DSL form.
  --root_num ROOT_NUM   Number of root objects(can be only in USER part of tuple) that need to be created. Default 1.
  --node_num NODE_NUM   Number of node objects(can be both in USER or OBJECT part of tuple) that need to be created.
                        Default 1.
  --leaf_num LEAF_NUM   Number of leaf objects(can be only in OBJECT part of tuple) that need to be created. Default
                        1.
  --user_num USER_NUM   Number of users that need to be created for each user relation. Default 1.
  --make_pub_obj        Make at least 1 object publicly available if it possible due your model.
  --make_wrong_tuples   Make some tuples incorrect.
  --user_type USER_TYPE
                        How users called in your model. Default 'user'.

Output: 3 files
objects.json - list of objects and relations between them (except of users). This file you should load
to your openFGA instance.
users.json - list of direct relationships between users and objects. This file you should
load to your openFGA instance.
users_4_test.json - list of all possible relationships between users and objects. May
contain wrong relationships, if you set flag make_wrong_tuples to true. You can use these tuples to make test requests
to your openFGA instance.
```
