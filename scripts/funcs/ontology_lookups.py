from owlready2 import *
import pandas as pd

def get_direct_descendants(ontology, iri, entity, names = True):
    """
    Get direct descendants of an entity in an ontology
    """
    onto = get_ontology(ontology).load()
    namespace = get_namespace(iri)

    entity = namespace[entity]

    descendants = [descendant.name.replace('obo.', '') for descendant in entity.subclasses()]
    if names:
        names = [descendant.label[0] for descendant in entity.subclasses()]
        descendants = pd.DataFrame({'Ontology ID': descendants, 'Name': names})
    else:
        descendants = pd.DataFrame(descendants, columns = ['Ontology ID'])

    return descendants

def get_all_descendants(ontology, iri, entity, names = False):
    """
    Get all descendants of an entity in an ontology
    """
    onto = get_ontology(ontology).load()
    namespace = get_namespace(iri)

    entity = namespace[entity]

    descendants = [descendant.name.replace('obo.', '') for descendant in entity.descendants()]
    if names == True:
        names = [descendant.label[0] for descendant in entity.descendants()]
        descendants = pd.DataFrame({'Ontology ID': descendants, 'Name': names})
    else:
        descendants = pd.DataFrame(descendants, columns = ['Ontology ID'])

    return descendants

def get_all_ancestors(ontology, iri, entity):
    """
    Get all ancestors of an entity in an ontology
    """
    onto = get_ontology(ontology).load()
    namespace = get_namespace(iri)

    entity = namespace[entity]

    all_ancestors = {ancestor.name.replace('obo.', '') for ancestor in entity.ancestors()}

    return all_ancestors

def main():
    #Directly access functions to quickly test them
    ontology = 'http://purl.obolibrary.org/obo/mondo.owl'
    namespace = 'http://purl.obolibrary.org/obo/'
    entity = 'MONDO_0700096'

    direct_descendants = get_direct_descendants(ontology, namespace, entity)

    print(direct_descendants)

if __name__ == '__main__':
    main()


    
