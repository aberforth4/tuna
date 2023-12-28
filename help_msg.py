desc_help = ("Tuna - tool that can generate for you tuples to test your OpenFGA authorization model "
             "in DSL form.")
mod_help = "--mod=PATH_2_MODEL_FILE Always required. Path to file with your OpenFGA authorization model in DSL form."
root_num_help = "Number of root objects(can be only in USER part of tuple) that need to be created. Default 1."
node_num_help = ("Number of node objects(can be both in USER or OBJECT part of tuple) that need to "
                 "be created. Default 1.")
leaf_num_help = ("Number of leaf objects(can be only in OBJECT part of tuple) that need to be "
                 "created. Default 1.")
user_num_help = "Number of users that need to be created for each user relation. Default 1."
make_pub_obj_help = "Make at least 1 object publicly available if it possible due your model."
make_wrong_tuples_help = "Make some tuples incorrect."
user_type_help = "How users called in your model. Default 'user'."

epilog_help = """Output: 
3 files objects.json - list of objects and relations 
between them (except of users). This file you should load to your openFGA instance. 
users.json - list of direct 
relationships between users and objects. This file you should load to your openFGA instance. 
users_4_test.json - list of all possible relationships between users and objects. May contain wrong relationships, if you set flag 
make_wrong_tuples to true. You can use these tuples to make test requests to your openFGA instance."""

