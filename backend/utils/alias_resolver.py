import requests

def resolve_gene_alias_to_official(gene_alias: str, species_taxon_id: int = 9606) -> str:
    """
    Resolve a gene alias to its official symbol using the UniProtKB Search API.
    Works for common aliases like 'NRF2' → 'NFE2L2'.
    """
    base_url = "https://rest.uniprot.org/uniprotkb/search"
    query = f"gene_exact:{gene_alias} AND organism_id:{species_taxon_id}"

    try:
        # === 1. Send a search request to UniProtKB ===
        response = requests.get(
            base_url,
            params={
                "query": query,
                "fields": "gene_primary,gene_names,organism_id",
                "format": "json",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

    except Exception as e:
        raise RuntimeError(f"Failed to query UniProt for '{gene_alias}': {e}")

    # === 2. Parse the search results ===
    results = data.get("results", [])
    if not results:
        raise ValueError(f"No UniProt entries found for alias: {gene_alias}")

    # === 3. Extract the gene information ===
    genes = results[0].get("genes", [])
    if not genes:
        raise ValueError(f"No gene information found for alias: {gene_alias}")

    # === 4. Return the official gene symbol ===
    for gene in genes:
        if "geneName" in gene:
            return gene["geneName"]["value"]

    raise ValueError(f"Official gene name not found for alias: {gene_alias}")