import random
import json


class ObjectGenerator:
    """Generate tuples for tests"""

    def __init__(self, user_obj_name,
                 root_num,
                 node_num,
                 leaf_num):
        self.__user_obj_name = user_obj_name
        self.__id_list = []
        self.root_num = root_num
        self.node_num = node_num
        self.leaf_num = leaf_num

    def generate_objects(self, auth_model_json: dict) -> list:
        """Make objects and user from auth model"""
        auth_model_json = auth_model_json["types"]
        roots = []
        tuples = []
        for obj in auth_model_json:
            if self.__define_type_of_obj_4_tree(obj, auth_model_json) == "root":
                roots.append(obj)
        for root in roots:
            tuples += self.__set_up_tree_root(root, auth_model_json)
        tuples += self.__set_up_rel_specific_rels(tuples, auth_model_json)
        return tuples

    def __can_object_establish_rel(self, obj_type: str, auth_model_json: list) -> bool:
        """Checks whether object of obj_type can establish relation as user or not"""
        if obj_type == self.__user_obj_name:
            return False
        for obj in auth_model_json:
            for rel in obj["relations"]:
                for can_rel_with in rel["can_relate_with"]:
                    if can_rel_with["type"] == "direct":
                        if can_rel_with["object"] == obj_type:
                            return True
        return False

    def __generate_id(self) -> int:
        """Generates unique ID for object"""
        while True:
            obj_id = random.randint(0, 99999999)
            if obj_id in self.__id_list:
                continue
            else:
                self.__id_list.append(obj_id)
                return obj_id

    def __define_type_of_obj_4_tree(self, obj_type, auth_model_json):
        """Specifies which element of the tree can be an object of type obj_type """
        if not self.__can_object_establish_rel(obj_type["name"], auth_model_json):
            return "leaf"
        if self.__is_object_tree_root(obj_type, auth_model_json):
            return "root"
        return "node"

    def __is_object_tree_root(self, obj_type, auth_model_json):
        if len(obj_type["relations"]) == 0:
            return False
        for rel in obj_type["relations"]:
            for can_relate_with in rel["can_relate_with"]:
                if can_relate_with["type"] == "direct":
                    if can_relate_with["object"] != self.__user_obj_name:
                        if can_relate_with["object"] != obj_type["name"]:
                            return False
        for obj in auth_model_json:
            if obj["name"] == obj_type["name"]:
                continue
            for rel in obj["relations"]:
                for can_relate_with in rel["can_relate_with"]:
                    if can_relate_with["type"] == "direct":
                        if can_relate_with["object"] == obj_type["name"]:
                            return True
        return False

    def __set_up_tree_root(self, obj_type:dict, auth_model_json: list) -> list:
        """Setting up root for tuple tree"""
        tuples = []
        tree_root_descs = []
        for i in range(self.root_num):
            tree_root_descs.append(f'{obj_type["name"]}:{self.__generate_id()}')
        #tree_root_desc = f'{obj_type["name"]}:{self.__generate_id()}'
        for rel in obj_type["relations"]:
            for can_relate_with in rel["can_relate_with"]:
                if can_relate_with["type"] == "direct":
                    if can_relate_with["object"] == obj_type["name"]:
                        # for situations where object can relate to object with the same type
                        # 4 example folder that can be a parent for another folder
                        tree_root_descs = []
                        for i in range(self.root_num):
                            tree_root_desc = f'{obj_type["name"]}:{self.__generate_id()}'
                            tree_root_descs.append(tree_root_desc)
                            tuples.append({
                                "user": f'{obj_type["name"]}:{self.__generate_id()}',
                                "relation": rel["name"],
                                "object": tree_root_desc
                            })
        for tree_root_desc in tree_root_descs:
            tuples += self.__set_up_whole_tree(tree_root_desc, auth_model_json)
        return tuples

    def __set_up_whole_tree(self, obj_desc_str: str, auth_model_json: list) -> list:
        """Setting up tuple tree by root or node given"""
        # obj_desc_str is a string that describes root|node object in format TYPE:ID
        obj_name = obj_desc_str.split(":")[0]
        tuples = []
        for obj in auth_model_json:
            if obj["name"] == obj_name:
                continue
            if obj["name"] == self.__user_obj_name:
                continue
            for rel in obj["relations"]:
                for can_relate_with in rel["can_relate_with"]:
                    if can_relate_with["type"] == "direct":
                        if can_relate_with["object"] == obj_name:
                            match self.__define_type_of_obj_4_tree(obj, auth_model_json):
                                case "leaf":
                                    for i in range(self.leaf_num):
                                        tuples.append(
                                            {
                                                "user": obj_desc_str,
                                                "relation": rel["name"],
                                                "object": f'{obj["name"]}:{self.__generate_id()}'
                                            }
                                        )
                                case "node":
                                    for i in range(self.node_num):
                                        child_id = self.__generate_id()
                                        tuples.append(
                                            {
                                                "user": obj_desc_str,
                                                "relation": rel["name"],
                                                "object": f'{obj["name"]}:{child_id}'
                                            }
                                        )
                                        tuples += self.__set_up_whole_tree(f'{obj["name"]}:{child_id}', auth_model_json)
        return tuples

    def __set_up_rel_specific_rels(self, tuples: list, auth_model_json: list) -> list:
        """For every object set up relation specific relation if it is possible.
        Relation specific relation looks like viewer: [group#member]"""
        objects = []
        rel_specific = []
        for tpl in tuples:
            if tpl["user"] not in objects:
                objects.append(tpl["user"])
            if tpl["object"] not in objects:
                objects.append(tpl["object"])
        for obj in objects:
            obj_type = obj.split(":")[0]
            for obj_model in auth_model_json:
                if obj_model["name"] == obj_type:
                    for rel in obj_model["relations"]:
                        for can_relate_with in rel["can_relate_with"]:
                            if can_relate_with["type"] == "relation_specific":
                                for i in range(self.leaf_num):
                                    rel_specific.append({
                                        "user": f'{can_relate_with["object_for_rel"]}:{self.__generate_id()}#{can_relate_with["needed_rel"]}',
                                        "relation": rel["name"],
                                        "object": obj
                                    })
        return rel_specific


