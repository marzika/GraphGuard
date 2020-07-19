from androguard.core.analysis.analysis import FieldAnalysis, ClassAnalysis

from collections import Counter, defaultdict

from formats import type_descriptors
from matching.matcher import Matcher


class StructureMatcher(Matcher):
    def get_exact_structure_matches(self, unmatched_cs):
        candidates = defaultdict(set)
        criteria = [
            ClassAnalysis.get_nb_methods,
            lambda ca: len(list(filter(lambda x: x.get_field().get_class_name() == ca.name, ca.get_fields()))),
            lambda ca: str(get_field_counter(ca)),
            get_method_set
        ]
        for c in unmatched_cs:
            if c.startswith("Lcom/") and self.dx2.get_class_analysis(c) is not None:
                candidates[c].add(c)
                continue

            ca = self.dx.get_class_analysis(c)
            for ca2 in self.dx2.get_classes():
                for cr in criteria:
                    if cr(ca) != cr(ca2):
                        break
                else:
                    candidates[c].add(ca2.name)

        return candidates


def get_usable(class_name):
    if class_name.startswith("["):
        return "[" + get_usable(class_name[1:])

    if class_name.startswith("Ljava/") or class_name.startswith("Landroid/") or class_name in type_descriptors.values():
        return class_name
    return "obfuscated.class"


def get_field_counter(ca):
    li = []
    for f in map(FieldAnalysis.get_field, ca.get_fields()):
        if ca.name != f.get_class_name():
            continue

        li.append(get_usable(str(f.get_descriptor())))
    return Counter(li)


def get_usable_description(ma):
    stripped, r = str(ma.descriptor[1:]).split(")")
    return "(" + (" ".join(map(get_usable, stripped.split(" "))) if stripped else "") + ")" + get_usable(r)


def get_method_set(ca):
    return {get_usable_description(m) for m in ca.get_methods()}