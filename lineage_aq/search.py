from lineage_aq.config import alternate_spells


def mark_alternate_spells_tokens(x: str) -> str:
    """
    Enclose the alternate_spells tokens contained in the given string by `()`.

    Example
    -------
    (global) alternate_spells = [
        ["ee", "i"],
        ["aa", "a"],
    ]

    >>> generate_formattable_str("Hadees")
    H(a)d(ee)s
    """

    found_tokens = []
    i = 0
    for group in alternate_spells:
        for item in group:
            if item in x:
                found_tokens.append(item)
                # This is done so that there should be no replacement
                # in the already grabbed text
                x = x.replace(item, f"({i})")
                i += 1

    for i, item in enumerate(found_tokens):
        x = x.replace(f"({i})", f"({item})")
    return x


def create_variants(x: str) -> set[str]:
    """
    Create all the variants(permutations) by replacing the marked tokens by their alternates.

    Parameter
    ---------
    x: str
        String with marked tokens [output of function mark_alternate_spells_tokens()]

    Returns
    -------
    variants: set[str]
        set containing all variants

    Example
    -------
    (global) alternate_spells = [
        ["ee", "i"],
        ["aa", "a"],
    ]

    >>> create_variants("H(a)d(ee)s")
    {'Hadees', 'Haadees', 'Haadis', 'Hadis'}
    """

    variants = {x.replace("(", "").replace(")", "")}

    start = x.find("(")
    end = x.find(")")
    while start >= 0:
        spell = x[start + 1 : end]

        group_ = []
        for group in alternate_spells:
            if spell in group:
                group_ = group.copy()
                group_.remove(spell)
                break

        for sim in group_:
            a = x[:start] + sim + x[end + 1 :]
            variants |= create_variants(a)

        x = x.replace("(", "", 1).replace(")", "", 1)

        start = x.find("(")
        end = x.find(")")

    return variants


def advanced_search(search_term: str, search_space: list[str]) -> list[str]:
    """
    Search the given search_term in the given search_space, by generating several variants of the search_term.

    Parameters
    ----------
    search_term: str
        The term to be searched
    search_space: list
        List containing the data from which the term is to be searched

    Returns
    -------
    :list[str]
        List containing matching terms

    Example
    -------
    (global) alternate_spells = [
        ["ee", "i"],
        ["aa", "a"],
    ]

    >>> advanced_search("Hadees", ["Hadis", "Hadees", "Other"])
    ['Hadees', 'Hadis']
    """
    search_term = search_term.lower()
    variants = create_variants(mark_alternate_spells_tokens(search_term))

    result = []
    for variant in variants:
        for term in search_space:
            if variant in term.lower():
                result.append(term)
    return result
