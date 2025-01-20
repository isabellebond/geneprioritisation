from owlready2 import *
import pandas as pd

def load_ontology(ontology, namespace):
    """
    Load ontology
    """

    onto = get_ontology(ontology)
    namespace = get_namespace(namespace)

    if onto.loaded:
        print("Ontology is already loaded.")
    else:
        onto.load()
        print("Ontology was not loaded. Now loaded.")

    return onto, namespace

def get_term_from_label(namespace, label, ontology):
    """
    Get ontology term from label
    """
    result = namespace.search(label=label)
    if result:
        id = result[0]  # Returns the IRI of the first matching result
        id = str(id).replace('obo.','')  # Remove 'obo.' from the IRI
        id = id.replace(f'{ontology}.', '')  # Remove the ontology IRI from the IRI
        return id
    else:
        return None  # Return None if no result found
        
def get_direct_descendants(namespace, entity, names = True):
    """
    Get direct descendants of an entity in an ontology
    """

    entity = namespace[entity]

    descendants = [descendant.name.replace('obo.', '') for descendant in entity.subclasses()]
    if names:
        names = [descendant.label[0] for descendant in entity.subclasses()]
        descendants = pd.DataFrame({'Ontology ID': descendants, 'Name': names})
    else:
        descendants = pd.DataFrame(descendants, columns = ['Ontology ID'])

    return descendants

def get_all_descendants(namespace, entity, names = False):
    """
    Get all descendants of an entity in an ontology
    """
    print(namespace, entity)
    obo = get_namespace(namespace)
    entity = obo[entity]
    print(entity)

    descendants = [descendant.name.replace('obo.', '') for descendant in entity.descendants()]
    if names == True:
        names = [descendant.label[0] for descendant in entity.descendants()]
        descendants = pd.DataFrame({'Ontology ID': descendants, 'Name': names})
    else:
        descendants = pd.DataFrame(descendants, columns = ['Ontology ID'])

    return descendants

def get_all_ancestors(namespace,entity):
    """
    Get all ancestors of an entity in an ontology
    """
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


    
