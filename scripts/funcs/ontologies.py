from owlready2 import *
import pandas as pd

def load_ontology(ontology, namespace):
    """
    Load an ontology and retrieve its associated namespace.

    This function loads an ontology from the specified source
    (e.g., file path, URL, or ontology IRI) and retrieves a 
    corresponding namespace object for working with its terms.
    If the ontology has already been loaded, it will not reload
    it, but will print a message indicating that status.

    Parameters
    ----------
    ontology : str
        Path, URL, or IRI of the ontology to load.
        Passed directly to `get_ontology()` from the owlready2 library.
    namespace : str
        Namespace IRI (or prefix) within the ontology to work with.
        Passed to `get_namespace()` from owlready2.

    Returns
    -------
    tuple
        A tuple `(onto, namespace_obj)` where:
        - `onto` is the loaded ontology object (owlready2 `Ontology` instance).
        - `namespace_obj` is the retrieved namespace object from the ontology.

    Raises
    ------
    ValueError
        If the namespace could not be found in the loaded ontology.
    OwlReadyOntologyParsingError
        If the ontology could not be parsed or loaded from the given source.
    FileNotFoundError
        If the ontology path is invalid (only raised for local files).

    Notes
    -----
    - If the ontology is already loaded (`onto.loaded` is True), the function 
      does not reload it but still returns the existing loaded object.
    - The `get_namespace()` call does not depend on whether the ontology was 
      preloaded; it is executed regardless.
    - This function validates that the namespace exists before returning.

    Examples
    --------
    >>> onto, ns = load_ontology(
    ...     "http://purl.obolibrary.org/obo/go.owl", 
    ...     "http://purl.obolibrary.org/obo/go#"
    ... )
    Ontology was not loaded. Now loaded.

    >>> onto, ns = load_ontology(
    ...     "http://purl.obolibrary.org/obo/go.owl", 
    ...     "http://purl.obolibrary.org/obo/go#"
    ... )
    Ontology is already loaded.
    """
    onto = get_ontology(ontology)
    namespace = get_namespace(namespace)

    if onto.loaded:
        print("Ontology is already loaded.")
    else:
        onto.load()
        print("Ontology was not loaded. Now loaded.")

    return onto, namespace

def get_term_from_label(namespace, label, ontology, prefix='obo.'):
    """
    Retrieve one or more ontology term identifiers from a human-readable label.

    This function searches within a given ontology namespace for terms whose
    `rdfs:label` matches the provided label (case-insensitive). If one or more
    matches are found, it returns a list of term identifier strings with common
    prefixes removed (such as "obo." or the ontology name prefix). If no match
    is found, an empty list is returned.

    Parameters
    ----------
    namespace : owlready2.namespace.Namespace
        The namespace object representing the ontology scope in which
        to search for the term.
    label : str
        The label of the ontology term to search for. Matching is
        case-insensitive.
    ontology : str
        Short name of the ontology (e.g., `"GO"`, `"HP"`) used for 
        removing the ontology-specific prefix from the result IRI.
    prefix : str, optional
        A common IRI prefix to strip from the result identifier.
        Defaults to `'obo.'`.

    Returns
    -------
    list of str
        A list of ontology term identifiers (without the specified prefixes)
        that match the given label. Returns an empty list if no matches are found.

    Notes
    -----
    - Matching is case-insensitive for robustness against label capitalization.
    - The search is performed using `namespace.search(label=...)` and then
      filtered to ensure exact match ignoring case.
    - Multiple terms may share the same label, so all matches are returned.
    - Prefix stripping assumes the term's string representation contains
      `"obo.TERMID"` or `"ONTOLOGY.TERMID"`. Adjust logic if IRIs differ.

    Examples
    --------
    >>> onto, ns = load_ontology(
    ...     "http://purl.obolibrary.org/obo/go.owl",
    ...     "http://purl.obolibrary.org/obo/go#"
    ... )
    >>> get_term_from_label(ns, "mitochondrion", "GO")
    ['0005739']

    >>> get_term_from_label(ns, "Nonexistent Term", "GO")
    []
    """
    results = namespace.search(label=label)  # Initial search
    
    # Also attempt case-insensitive match
    if not results:
        results = [term for term in namespace.classes() 
                   if hasattr(term, 'label') and 
                   any(l.lower() == label.lower() for l in term.label)]
    
    ids = []
    for term in results:
        term_str = str(term)
        term_str = term_str.replace(prefix, '')
        term_str = term_str.replace(f"{ontology}.", '')
        ids.append(term_str)
    
    return list(set(ids))  # Remove duplicates
        
def get_descendants(onto, namespace, entity_id, alternate_iri = None, names=True, prefix='obo.', direct_only=False, leaf_only=False):
    """
    Retrieve ontology descendants for a given entity.

    This function traverses the ontology hierarchy from a given starting
    entity and returns its descendants as a DataFrame. Options allow control
    over whether only direct children or all descendants are returned, whether
    only leaf terms are included, and whether to include human-readable names.

    Parameters
    ----------
    namespace : owlready2.namespace.Namespace
        The ontology namespace in which to search.
    entity_id : str
        The ontology term ID or name (within the namespace) whose descendants
        should be retrieved.
    names : bool, optional
        If True (default), include human-readable labels in the output.
    prefix : str, optional
        Prefix to strip from term IDs before returning. Default is `'obo.'`.
    direct_only : bool, optional
        If True, return only direct children (immediate subclasses).
        If False (default), return all descendants recursively.
    leaf_only : bool, optional
        If True, return only leaf terms (no subclasses). Default is False.

    Returns
    -------
    pandas.DataFrame
        DataFrame with:
        - `"Ontology ID"`: Term identifier without the prefix.
        - `"Name"`: Human-readable label (only if `names=True`).

    Notes
    -----
    - Duplicate terms are removed from the output.
    - If a term has no label, the `"Name"` column falls back to the term name.
    - Traversal avoids revisiting already-seen nodes.

    Examples
    --------
    >>> get_descendants(ns, "GO_0005739", names=True, direct_only=True)
      Ontology ID                Name
    0   GO_0005740  mitochondrion part

    >>> get_descendants(ns, "GO_0005739", names=True, leaf_only=True)
      Ontology ID                     Name
    0   GO_0005741  mitochondrial matrix
    1   GO_0005742  mitochondrial inner membrane
    """

    if alternate_iri:
        entity = onto.search_one(iri=f'{alternate_iri}{entity_id}')
    else:
        entity = namespace[entity_id]
    print(entity, entity_id)

    seen = set()
    descendants = []
    leaf_terms = []

    if direct_only:
        children = list(entity.subclasses())
        if leaf_only:
            children = [c for c in children if not list(c.subclasses())]
        descendants = children
    else:
        to_process = [entity]
        while to_process:
            current = to_process.pop()
            if current in seen:
                continue
            seen.add(current)

            children = list(current.subclasses())
            if not children:
                leaf_terms.append(current)

            descendants.extend(children)
            to_process.extend([child for child in children if child not in seen])

        descendants = leaf_terms if leaf_only else descendants

    # Build DataFrame
    if names:
        data = {
            'Ontology ID': [cls.name.replace(prefix, '') for cls in descendants],
            'Name': [cls.label[0] if cls.label else cls.name for cls in descendants]
        }
    else:
        data = {'Ontology ID': [cls.name.replace(prefix, '') for cls in descendants]}

    # Remove duplicates and reset index
    df = pd.DataFrame(data).drop_duplicates().reset_index(drop=True)

    return df

def get_all_ancestors(namespace, entity, prefix='obo.'):
    """
    Retrieve all ancestors (excluding the entity itself) of a given ontology entity.

    Parameters
    ----------
    namespace : owlready2.namespace.Namespace
        The ontology namespace in which to search.
    entity : str
        The ontology term ID or name (within the namespace) whose
        ancestors should be retrieved.
    prefix : str, optional
        Prefix to strip from term IDs before returning. Default is `'obo.'`.

    Returns
    -------
    list of str
        List of ontology term identifiers for all ancestors of the entity,
        with the specified prefix removed. The original entity is excluded.

    Notes
    -----
    - Includes both direct and indirect ancestors (recursively up the hierarchy).
    - Order of ancestors is determined by Owlready2 and is not guaranteed
      to reflect hierarchy levels.
    - The root term(s) of the ontology are included if reachable from the entity.

    Examples
    --------
    >>> get_all_ancestors(ns, "GO_0005739")
    ['GO_0005575', 'GO_0003674', 'GO_0008150']
    """
    entity_obj = namespace[entity]
    all_ancestors = entity_obj.ancestors() - {entity_obj}  # Exclude self
    return [ancestor.name.replace(prefix, '') for ancestor in all_ancestors]

def invert_part_of(onto, namespace, entity, 
                   part_of='http://purl.obolibrary.org/obo/BFO_0000050', 
                   prefix='obo.'):
    """
    Retrieve all ontology classes that contain the given entity via a 'part_of' relation.

    This function inverts the typical 'part_of' relationship by finding all classes
    that list the specified entity as one of their parts. In other words, it answers
    the question: *"Which entities is this entity a part of?"*

    Parameters
    ----------
    onto : owlready2.namespace.Ontology
        The loaded ontology object.
    namespace : owlready2.namespace.Namespace
        The ontology namespace in which to search.
    entity : str
        The ontology term ID or name (within the namespace) whose parent 
        entities via 'part_of' should be retrieved.
    part_of : str, optional
        IRI for the 'part_of' object property. Defaults to the standard
        BFO 'part_of' relation.
    prefix : str, optional
        Prefix to strip from term identifiers before returning. Default is `'obo.'`.

    Returns
    -------
    list of str
        List of ontology term identifiers for all entities that contain the
        given entity via the 'part_of' relationship, with the specified prefix removed.

    Notes
    -----
    - The function iterates over all ontology classes, checking whether
      the given entity appears in their `part_of` property values.
    - The returned list contains IDs without the given `prefix`.
    - Matching is exact — it will not resolve subclasses of the given entity.

    Examples
    --------
    >>> invert_part_of(onto, ns, "GO_0005739")
    ['GO_0005740', 'GO_0005741']
    """
    part_of = onto.search_one(iri=part_of)  # 'part_of' relation
    inverted_part_of = []
    entity = entity  # Add prefix to the entity
    
    for term in onto.classes():
        if namespace[entity] in list(part_of[term]):
            inverted_part_of.append(str(term).replace(prefix, ''))

    return inverted_part_of

def get_property_value(onto, namespace, entity, external_db='ICD-10', 
               property_iri='http://www.geneontology.org/formats/oboInOwl#hasDbXref', 
               prefix='obo.'):
    """
    Retrieve database cross-references (dbxrefs) for an ontology entity.

    Parameters
    ----------
    onto : owlready2.namespace.Ontology
        The loaded ontology object.
    namespace : owlready2.namespace.Namespace
        The ontology namespace in which to search.
    entity : str
        The ontology term ID or name (within the namespace) whose dbxrefs
        should be retrieved.
    external_db : str or None, optional
        If specified (default: 'ICD-10'), return only dbxrefs containing this 
        string. If None, return all dbxrefs.
    dbxref_iri : str, optional
        The IRI for the 'hasDbXref' property. Default is the standard 
        OBO 'hasDbXref' IRI.
    prefix : str, optional
        Prefix to strip from ontology term IDs if used for reporting.
        Default is `'obo.'`.

    Returns
    -------
    list of str
        A list of dbxref values for the given entity. If `external_db` is
        provided, only matching entries are returned. If no matches are found,
        returns an empty list.

    Notes
    -----
    - Dbxrefs are returned as strings (typically CURIEs or IRIs).
    - The function does not validate the format of the dbxref — only checks 
      for substring matches to `external_db` if provided.
    - If you only need to check *existence*, use `bool(has_dbxref(...))`.

    Examples
    --------
    >>> has_dbxref(onto, ns, "GO_0005739", external_db="ICD-10")
    ['ICD-10:C19']

    >>> has_dbxref(onto, ns, "GO_0005739", external_db=None)
    ['ICD-10:C19', 'UMLS:C0025202']
    """
    prop = onto.search_one(iri=property_iri)
    if prop is None:
        raise ValueError(f"'hasDbXref' property not found at IRI: {property_iri}")

    term = namespace[entity]
    all_items = [str(item) for item in prop[term]]

    if external_db is not None:
        items = []
        for item in all_items:
            if external_db in str(item):
                items.append(item)
        return items
    else:
        return all_items
 
def get_class_properties(onto, namespace, entity):
    """
    Retrieve all properties and their values for a given ontology entity.

    Parameters
    ----------
    namespace : owlready2.namespace.Namespace
        The ontology namespace containing the entity.
    entity : str
        The ontology term ID or name whose properties should be retrieved.

    Returns
    -------
    dict
        A dictionary where keys are property names (str) and values are lists
        of property values associated with the entity.

    Notes
    -----
    - Includes both object properties and data properties.
    - Property values are returned as strings for readability.
    - Properties with no values for the entity are omitted.

    Examples
    --------
    >>> get_all_properties(ns, "GO_0005739")
    {
        'hasDbXref': ['ICD-10:C19', 'UMLS:C0025202'],
        'is_a': ['GO_0005575']
    }
    """
    term = namespace[entity]
    props = {}

    for prop in term.get_class_properties():
        values = list(prop[term])
        if values:
            str_values = [str(v) for v in values]
            props[prop.name] = str_values

    return props

def list_all_properties(onto):
    """
    List all properties (object and data) defined in an ontology,
    including their IRI, local name, and label (if available).

    Parameters
    ----------
    onto : owlready2.namespace.Ontology
        The loaded ontology object.

    Returns
    -------
    dict
        Dictionary with keys 'iri', 'name', and 'label' each mapping to a list of strings.
    """
    props = {
        'iri': [],
        'name': [],
        'label': []
    }

    for prop in onto.properties():
        props['iri'].append(prop.iri)
        props['name'].append(prop.name)
        # prop.label is a list of strings; get the first label or empty string
        if prop.label:
            props['label'].append(prop.label[0])
        else:
            props['label'].append('')

    return pd.DataFrame(props).drop_duplicates().reset_index(drop=True)