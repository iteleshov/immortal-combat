# https://github.com/Augmented-Nature/Augmented-Nature-UniProt-MCP-Server
# How to run the server:
# docker build -t uniprot-mcp-server .
# docker run -i uniprot-mcp-server
# or
# git clone <repository-url>
# cd uniprot-server
# npm install
# npm run build


from smolagents import ToolCollection, ToolCallingAgent, OpenAIServerModel
from mcp import StdioServerParameters
import os


# configuration
def set_server(server_name="uniprot-mcp-server"):
    server = StdioServerParameters(
        command="docker",
        args=["exec", "-i", server_name, "node", "/app/build/index.js"]
    )
    return server


def set_model(
    api_key=os.environ["NEBIUS_API_KEY"],
    api_base="https://api.studio.nebius.com/v1/",
    temperature=0,
    model_name="Qwen/Qwen3-235B-A22B-Instruct-2507"
):
    model = OpenAIServerModel(
        model_id=model_name,
        api_key=api_key,
        api_base=api_base,
        temperature=temperature,
    )
    return model


SYSTEM_PROMPT = """
You are a bioinformatics research agent connected exclusively to the Augmented-Nature-UniProt-MCP-Server.

Your task is to retrieve precise protein information from UniProt and its linked databases for a given gene or protein name.

Scope of retrieval:
1. Canonical UniProt entry (include a FASTA link, not the raw sequence).
2. Isoforms (alternative splicing) — names, UniProt IDs, and lengths.
3. Functional regions and sequence features — domains, motifs, regions, sites, mutagenesis.
4. Natural variants and mutagenesis experiments with described functional effects.
5. Post-translational modifications (PTMs) such as phosphorylation, acetylation, methylation, ubiquitination, etc.
6. Subcellular location annotations.
7. Cross-references: HGNC, Ensembl, PDB, Reactome, Gene Ontology (GO), KEGG.

Rules:
- Use **only** data obtained directly from MCP tools (e.g., `search_proteins`, `get_protein_info`, `get_protein_features`, `get_cross_references`).
- **Do not guess or fabricate** any facts not explicitly found in tool outputs.
- Keep biological names and identifiers exactly as in UniProt.
- Prefer full lists if multiple values exist.
"""

def set_user_prompt(gene_or_protein_name):
    return f"""
Protein: {gene_or_protein_name}

Retrieve all available UniProt data per the scope above, using only MCP tool outputs. 
Do not invent or infer missing information.
Search recommendations: Use more than 1 search results. String indices must be integers, not 'str'.
Rules and priorities:
1. **Always prefer reviewed (Swiss-Prot) entries** over unreviewed (TrEMBL) ones when both exist.
2. If the search results include multiple entries, select the one explicitly marked as “UniProtKB reviewed (Swiss-Prot)” — this is the canonical human record.
3. Never claim that data is “missing” if a reviewed canonical entry was found.
4. If both a fragment and a full canonical entry are present, use the full reviewed one and ignore the fragment.
5. Use only the information retrieved from MCP tool outputs. Do not add facts from external knowledge.
6. If no reviewed entry is found at all, then and only then mention that data may be incomplete.

When writing the summary:
- Use bullet points or short factual sentences under each section.
- Include FASTA links and UniProt IDs where available.
- Do not include commentary about the search process or tool execution.
- Do not add speculative language like “may be”, “possibly”, “appears to”.
- All information must be based ONLY on the data retrieved by via tools. 
If any of the sections are unavailable print "Info unavailable" - do not invent facts.

Write a concise, readable plain-text summary of the retrieved UniProt data.
Stick to this structure in output:
1. **Canonical sequence and isoforms**
   - Retrieve the canonical FASTA sequence and all annotated isoforms (alternative splicing variants).  
   - Note sequence length and UniProt accession for each.

2. **Functional sequence intervals**
   - From `features`: list all annotated *regions, domains, motifs, sites,* and *mutagenesis* entries.  
   - For each, include:
     • name of interval  
     • amino-acid positions  
     • description or known binding partner  
     • experimental notes (e.g., “loss of KEAP1 binding”, “increased transcriptional activity”).

3. **Natural variants and mutagenesis data**
   - Extract annotated variants and experimental mutagenesis results.  
   - For each, specify: position → substitution → observed functional consequence (e.g. “S40A — abolishes phosphorylation”).  
   - Focus on those affecting activity, binding, or stability.

4. **Post-translational modifications (PTM)**
   - Summarize all PTM annotations (phosphorylation, acetylation, ubiquitination, etc.) with residue positions and known effect on function.

5. **Cross-references**
   - Include available cross-links to HGNC, Ensembl, PDB, Reactome, Gene Ontology, and KEGG.  
   - Briefly describe what each reference contributes (e.g. “Reactome → NRF2 pathway in oxidative stress response”).

6. **Subcellular location**
   - State primary and secondary locations from UniProt annotation (e.g. “Cytoplasm → Nucleus translocation upon activation”).  
   - Note relevance to function or degradation (e.g. “KEAP1-mediated cytoplasmic retention”).

7. **Longevity relevance**
   - When possible, highlight how these functional regions or variants are implicated in lifespan regulation (e.g. “Neoaves KEAP1 mutation → constitutive NRF2 activation → increased stress resistance”).

When calling MCP tools, use only the UniProt tools available in the current MCP server (e.g., `bc_search_uniprot_entries`, `bc_get_uniprot_entry`, `bc_get_uniprot_features`, `bc_get_uniprot_variants`, `bc_get_uniprot_crossrefs`, `bc_get_uniprot_subcellular_location`, etc. — depending on implementation).

Return concise, human-readable research text suitable for direct inclusion into a WikiCrow-style article.  
Do **not** output JSON or code blocks — only clean text with section headers.
"""

def run_query(
    gene,
    server=set_server(),
    model=set_model(),
    trust_remote_code=True,
    structured_output=False
):
    system_prompt = SYSTEM_PROMPT
    user_prompt = set_user_prompt(gene)
    with ToolCollection.from_mcp(
        server_parameters=server,
        trust_remote_code=trust_remote_code,
        structured_output=structured_output
    ) as tools:
        agent = ToolCallingAgent(
            model=model,
            tools=[*tools.tools],
            add_base_tools=False,
            max_steps=1,
        )
        agent.prompt_templates["system_prompt"] = system_prompt
        result = agent.run(user_prompt)

    return result
