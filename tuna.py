from auth_model_parser import AuthModelParser
import json
from object_generator import ObjectGenerator
from user_generator import UserGenerator
from help_msg import *
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=desc_help, epilog=epilog_help)
    parser.add_argument('--mod', help=mod_help, type=argparse.FileType('r'), required=True)
    parser.add_argument('--root_num', help=root_num_help, type=int, required=False, default=1)
    parser.add_argument('--node_num', help=node_num_help, type=int, required=False, default=1)
    parser.add_argument('--leaf_num', help=leaf_num_help, type=int, required=False, default=1)
    parser.add_argument('--user_num', help=user_num_help, type=int, required=False, default=1)
    parser.add_argument('--make_pub_obj', help=make_pub_obj_help, action='store_true', required=False)
    parser.add_argument('--make_wrong_tuples', help=make_wrong_tuples_help, action='store_true', required=False)
    parser.add_argument('--user_type', help=user_type_help, type=str, required=False, default='user')

    args = parser.parse_args()

    auth_model_parser = AuthModelParser()
    model = auth_model_parser.parse_model_from_file(args.mod)

    object_generator = ObjectGenerator(args.user_type, args.root_num, args.node_num, args.leaf_num)
    objects_tuples = object_generator.generate_objects(model)

    user_generator = UserGenerator(args.user_type, args.user_num)
    user_tuples = user_generator.generate_users(objects_tuples, model)
    user_tuples_4_test = user_generator.generate_all_users_rels(objects_tuples, user_tuples, model)

    if args.make_pub_obj:
        user_tuples_4_test = user_generator.make_public_objects(user_tuples, objects_tuples, model)

    if args.make_wrong_tuples:
        user_tuples_4_test = user_generator.make_wrong_tuples(user_tuples_4_test)

    f = open("users_4_test.json", "w")
    json.dump(user_tuples_4_test, f, indent=4)
    f.close()

    f = open("users.json", "w")
    json.dump(user_tuples, f, indent=4)
    f.close()

    f = open("objects.json", "w")
    json.dump(objects_tuples, f, indent=4)
    f.close()


