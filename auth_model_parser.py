import re


class AuthModelParser():
    def parse_model_from_file(self, f) -> dict:
        """Конвертирует модель авторизации на dsl в список json объектов"""
        dsl_model = f.read()
        f.close()
        dsl_model = dsl_model.replace("\n", "")
        dsl_model = dsl_model.split("type")
        dsl_model.pop(0)
        json_model = {
            "types": []
        }
        for obj_type in dsl_model:
            json_model["types"].append(self.__parse_single_type(obj_type))
        return json_model

    def __parse_single_type(self, dsl_str: str) -> dict:
        """Конвертирует dsl описание объекта в json"""
        dsl_str = dsl_str.split("relations")
        single_type = {
            "name": dsl_str[0].replace(" ", ""),
            "relations": []
        }
        dsl_str.pop(0)

        if len(dsl_str) == 0:
            return single_type
        dsl_str = dsl_str[0].split("define")
        dsl_str.pop(0)
        for relation in dsl_str:
            single_type["relations"].append(self.__parse_single_relation(relation))
        return single_type

    def __parse_single_relation(self, rel: str) -> dict:
        """Парсит отношение объекта в json формат"""
        relation = {
            "name": "",
            "can_relate_with": []
        }
        rel_name_index = rel.find(":")
        relation_name = rel[:rel_name_index].replace(" ", "")
        if not relation_name:
            print("Incorrect model")
            exit()
        relation["name"] = relation_name
        rel = rel[rel_name_index + 2:]
        # сначала смотрим, есть в описании отношения прямые указания на типы
        # которые могут установить такое отношение. Они указаны в []
        direct_relationship = re.findall(r'\[(.*)\]', rel)
        if len(direct_relationship) == 1:
            relation["can_relate_with"] += self.__parse_direct_relationship(direct_relationship[0])
            rel = rel.replace(f'[{direct_relationship[0]}]', "")
        if rel.find("from") != -1:
            for rel_name in rel.split(" or "):
                if len(rel_name) == 0:
                    continue
                if rel_name.find("from") == -1:
                    relation["can_relate_with"].append(
                        {
                            "type": "this",
                            "relation_needed": rel_name,
                        }
                    )
                else:
                    tmp = rel_name.split(" from ")
                    relation_from = tmp[1].replace(" ", "")
                    relation["can_relate_with"].append(
                        {
                            "type": "indirect",
                            "relation_needed": tmp[0],
                            "relation_from": relation_from
                        }
                    )
        else:
            for or_part in rel.split(" or "):
                if len(or_part.replace(" ", "")) != 0:
                    relation["can_relate_with"].append(
                        {
                            "type": "this",
                            "relation_needed": or_part.replace(" ", "")
                        }
                    )
        return relation

    def __parse_direct_relationship(self, rel: str) -> list:
        """Парсит прямые отношения объекта в json формат"""
        rel = rel.split(",")
        direct_rels = []
        for obj_type in rel:
            obj_type = obj_type.replace(" ", "")
            if obj_type.find(":*") != -1:
                # public отношение
                direct_rels.append(
                    {
                        "type": "public",
                        "object": obj_type.split(":")[0]
                    }
                )
            if obj_type.find("#") != -1:
                tmp = obj_type.split("#")
                direct_rels.append(
                    {
                        "type": "relation_specific",
                        "object_for_rel": tmp[0],
                        "needed_rel": tmp[1]
                    }
                )
            if obj_type.find("#") == -1 and obj_type.find(":*") == -1:
                direct_rels.append(
                    {
                        "type": "direct",
                        "object": obj_type
                    }
                )
        return direct_rels
