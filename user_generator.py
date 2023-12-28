import random
import json


class UserGenerator:
    """Generate users for tests"""

    def __init__(self, user_obj_name, user_num):
        self.__user_obj_name = user_obj_name
        self.__id_list = []
        self.__user_num = user_num

    def generate_users(self, tuples: list, auth_model_json: dict) -> list:
        """Make objects and user from auth model"""
        auth_model_json = auth_model_json["types"]
        objects = self.__make_objects_list(tuples)
        user_tuples = []
        for obj in objects:
            if obj.find("#") != -1:
                user_tuples += self.__create_users_4_rel_sp_relation(obj)
            else:
                user_tuples += self.__create_direct_related_users(obj, auth_model_json)
        return user_tuples

    def generate_all_users_rels(self, tuples: list, user_tuples: list, auth_model_json: dict) -> list:
        """Generates all possible user to objects relation based on model, objects, and
        direct user to object relations"""
        auth_model_json = auth_model_json["types"]
        objects = self.__make_objects_list(tuples)
        for obj in objects:
            if obj.find("#") != -1:
                usr_tpls = self.__find_users_4_rel_sp_relation(obj, user_tuples)
                for usr_tpl in usr_tpls:
                    user_tuples += self.__create_rels_4_sp_related_usr(usr_tpl, obj, tuples, auth_model_json)
        user_indirect_rels = []
        for usr_tpl in user_tuples:
            user_indirect_rels += self.__get_user_rel_tuples(usr_tpl, tuples, auth_model_json)
        user_tuples += user_indirect_rels
        return user_tuples

    def make_public_objects(self, user_tuples: list, obj_tuples: list, auth_model_json: dict) -> list:
        """If it is possible by model make 1 or half of objects of each type publicly accessible."""
        objects = self.__make_objects_list(obj_tuples)
        auth_model_json = auth_model_json["types"]
        types_that_can_be_public = self.__find_types_that_can_be_public(auth_model_json)
        for public_type in types_that_can_be_public:
            objects_for_public = self.__find_all_objects_by_type(public_type[0], objects)
            seek_in = objects
            if public_type[1] == self.__user_obj_name:
                seek_in = self.__get_user_list(user_tuples)
            pub_obj_num = len(objects_for_public) // 2
            if pub_obj_num == 0:
                pub_obj_num += 1
            for i in range(pub_obj_num):
                pub_tuple = {
                    "user": f'{public_type[1]}:*',
                    "relation": public_type[2],
                    "object": objects_for_public[i]
                }
                user_tuples.append(pub_tuple)
                public_tuples = self.__make_tuples_4_public_access(pub_tuple, public_type[1], seek_in)
                for tpl in public_tuples:
                    if tpl["user"].find("*") != -1:
                        continue
                    user_tuples.append(tpl)
                    user_tuples += self.__get_user_rel_tuples(tpl, obj_tuples, auth_model_json)
        return user_tuples

    def make_wrong_tuples(self, user_tuples: list) -> list:
        """Make some tuples in user_tuples wrong"""
        users = self.__get_user_list(user_tuples)
        wrong_tpl_num = len(user_tuples) // 3
        for i in range(wrong_tpl_num):
            tpl_2_change = random.choice(user_tuples)
            tpl_2_change["user"] = f'{random.choice(users)}'
        return user_tuples
    def __generate_id(self) -> int:
        """Generates unique ID for object"""
        while True:
            obj_id = random.randint(0, 99999999)
            if obj_id in self.__id_list:
                continue
            else:
                self.__id_list.append(obj_id)
                return obj_id

    def __get_object_from_auth_model(self, obj_type: str, auth_model_json: list) -> dict:
        """Extract object from auth model json"""
        for obj in auth_model_json:
            if obj["name"] == obj_type:
                return obj
        return {}

    def __create_direct_related_users(self, obj: str, auth_model_json: list) -> list:
        """Create direct related users for given object"""
        obj_type = obj.split(":")[0]
        direct_users_tuples = []
        model_obj = self.__get_object_from_auth_model(obj_type, auth_model_json)
        for rel in model_obj["relations"]:
            for can_relate_with in rel["can_relate_with"]:
                if can_relate_with["type"] == "direct":
                    if can_relate_with["object"] == self.__user_obj_name:
                        direct_users_tuples.append({
                            "user": f'{self.__user_obj_name}:{self.__generate_id()}',
                            "relation": rel["name"],
                            "object": obj
                        })
        return direct_users_tuples

    def __get_user_rel_tuples(self, usr_tpl: dict, tuples: list, auth_model_json: list) -> list:
        """Extracts all user relations based on object tuple"""
        usr_relations = []
        init_object_type = usr_tpl["object"].split(":")[0]
        obj_model = self.__get_object_from_auth_model(init_object_type, auth_model_json)
        usr_rels_with_other = self.__get_rels_from_other_objs(usr_tpl, tuples)
        for usr_rel_with_other in usr_rels_with_other:
            usr_relations += self.__fill_user_indirect_rels(usr_tpl, usr_rel_with_other, tuples, auth_model_json)

        # establish all "this" type relations
        for rel in obj_model["relations"]:
            for can_relate_with in rel["can_relate_with"]:
                if can_relate_with["type"] == "this":
                    if can_relate_with["relation_needed"] == usr_tpl["relation"]:
                        found_rel = {
                            "user": usr_tpl["user"],
                            "relation": rel["name"],
                            "object": usr_tpl["object"]
                        }
                        usr_relations.append(found_rel)
                        usr_rels_with_other = self.__get_rels_from_other_objs(found_rel, tuples)
                        for usr_rel_with_other in usr_rels_with_other:
                            usr_relations += self.__fill_user_indirect_rels(found_rel, usr_rel_with_other, tuples,
                                                                            auth_model_json)
        return usr_relations

    def __fill_user_indirect_rels(self, usr_tuple, obj_rel_tuple, tuples, auth_model_json):
        """Check what relations with other objects gives relations from usr_tuple"""
        user_indirect_rels = []
        obj_type = obj_rel_tuple["object"].split(":")[0]
        model_obj = self.__get_object_from_auth_model(obj_type, auth_model_json)
        for rel in model_obj["relations"]:
            for can_relate_with in rel["can_relate_with"]:
                if can_relate_with["type"] == "indirect":
                    if obj_rel_tuple["relation"] == can_relate_with["relation_from"]:
                        if usr_tuple["relation"] == can_relate_with["relation_needed"]:
                            new_usr_tuple = {
                                "user": usr_tuple["user"],
                                "relation": rel["name"],
                                "object": obj_rel_tuple["object"]
                            }
                            user_indirect_rels.append(new_usr_tuple)
                            usr_rels_with_other = self.__get_rels_from_other_objs(new_usr_tuple, tuples)
                            for usr_rel_with_other in usr_rels_with_other:
                                user_indirect_rels += self.__fill_user_indirect_rels(new_usr_tuple, usr_rel_with_other,
                                                                                     tuples, auth_model_json)
        return user_indirect_rels

    def __get_rels_from_other_objs(self, usr_tuple: dict, tuples: list) -> list:
        """Gets relations of object from usr_tuple['object'] with other object in tuples list"""
        user_rels = []
        # check if user object have any relations to other objects as user
        for tpl in tuples:
            if tpl["user"] == usr_tuple["object"]:
                user_rels.append(tpl)
        return user_rels

    def __create_users_4_rel_sp_relation(self, obj_str: str) -> list:
        """Creates tuples for relation specific relation.
        Relation specific relation looks like viewer: [group#member].
        obj_str must look like group:82886295#member"""
        sp_rel_tuples = []
        tmp = obj_str.split("#")
        for i in range(self.__user_num):
            sp_rel_tuples.append({
                "user": f'{self.__user_obj_name}:{self.__generate_id()}',
                "relation": tmp[1],
                "object": tmp[0]
            })
        return sp_rel_tuples

    def __create_rels_4_sp_related_usr(self, usr_tpl: dict, obj_str: str, tuples: list,
                                       auth_model_json: list) -> list:
        """If user have relation_specific relation, maybe he will also have relation with other object.
        obj_str looks like group:66430646#member"""
        rels_4_sp_related_usr = []
        tmp = obj_str.split("#")
        for tpl in tuples:
            if tpl["user"] == obj_str:
                obj_model = self.__get_object_from_auth_model(tpl["object"].split(":")[0], auth_model_json)
                if obj_model == {}:
                    return []
                for rel in obj_model["relations"]:
                    for can_relate_with in rel["can_relate_with"]:
                        if can_relate_with["type"] == "relation_specific":
                            if tmp[1] == can_relate_with["needed_rel"]:
                                if tmp[0].split(":")[0] == can_relate_with["object_for_rel"]:
                                    rels_4_sp_related_usr.append({
                                        "user": usr_tpl["user"],
                                        "relation": rel["name"],
                                        "object": tpl["object"]
                                    })
        return rels_4_sp_related_usr

    def __make_objects_list(self, tuples: list) -> list:
        """Extracts all objects from tuples to list"""
        objects = []
        for tpl in tuples:
            if tpl["user"] not in objects:
                objects.append(tpl["user"])
            if tpl["object"] not in objects:
                objects.append(tpl["object"])
        return objects

    def __find_users_4_rel_sp_relation(self, obj_str: str, tuples: list) -> list:
        """Search for tuples created for relation specific relation.
                Relation specific relation looks like viewer: [group#member].
                obj_str must look like group:82886295#member"""
        rel_sp_relation_tuples = []
        tmp = obj_str.split("#")
        for tpl in tuples:
            if tpl["object"] == tmp[0]:
                if tpl["relation"] == tmp[1]:
                    rel_sp_relation_tuples.append(tpl)
        return rel_sp_relation_tuples

    def __get_user_list(self, user_tuples: list) -> list:
        """Get list of all created users"""
        users = []
        for tpl in user_tuples:
            if tpl["user"] not in users:
                users.append(tpl["user"])
        return users

    def __find_types_that_can_be_public(self, auth_model_json) -> list:
        """Search for objects that can be public"""
        public_types = []
        for obj in auth_model_json:
            for rel in obj["relations"]:
                for can_relate_with in rel["can_relate_with"]:
                    if can_relate_with["type"] == "public":
                        public_types.append((obj["name"], can_relate_with["object"], rel["name"]))
        return public_types

    def __find_all_objects_by_type(self, needed_type: str, objects: list) -> list:
        """Search for all objects of given type"""
        needed_objects = []
        for obj in objects:
            if obj.find("#") != -1:
                obj = obj.split("#")[0]
            if obj.split(":")[0] == needed_type:
                needed_objects.append(obj)
        return needed_objects

    def __make_tuples_4_public_access(self, pub_tuple: dict, type_4_access: str, objects: list) -> list:
        """Create tuples to establish relation with all objects of type_4_access
        If object from pub_tuple declared as public"""
        tuples_4_public_access = []
        objects_to_access = self.__find_all_objects_by_type(type_4_access, objects)
        for obj in objects_to_access:
            tuples_4_public_access.append({
                "user": obj,
                "relation": pub_tuple["relation"],
                "object": pub_tuple["object"]
            })
        return tuples_4_public_access
