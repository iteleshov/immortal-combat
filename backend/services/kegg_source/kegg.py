# How to launch MCP server 
# https://github.com/Augmented-Nature/KEGG-MCP-Server

from smolagents import ToolCollection, ToolCallingAgent, OpenAIServerModel
from mcp import StdioServerParameters
import os
import json


# config
os.environ['NEBIUS_API_KEY'] = open('secret.txt', 'r').read().strip()
def set_server():
    server = StdioServerParameters(
        command="node",
        args=["/mnt/c/Users/Uniholder/Git/KEGG-MCP-Server/build/index.js", "stdio"],
        cwd="/mnt/c/Users/Uniholder/Git/KEGG-MCP-Server"
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


SYSTEM_PROMPT = '''
You are a bioinformatics knowledge extraction agent connected exclusively to the KEGG MCP server.
Your task is to retrieve and summarize pathway- and function-level information for a given human gene or protein.

Focus on mapping between sequence-level identifiers (UniProt ID or HGNC symbol) and their KEGG pathways, modules, and processes.

For each gene/protein:
- Identify its KEGG entry (e.g. hsa:348 for APOE).
- Retrieve all associated KEGG pathways.
- For each pathway, extract:
  • pathway ID and name
  • short description
  • functional category (Metabolism, Genetic Information Processing, Environmental Information Processing, Cellular Processes, Organismal Systems, Human Diseases)
  • molecular function of the protein within this pathway
- Identify any pathways related to:
  “aging”, “longevity”, “oxidative stress”, “neurodegeneration”, “inflammation”, “FOXO”, “mTOR”, “AMPK”, “SIRT”, “autophagy”.
- If available, retrieve KEGG orthologs (KO identifiers) and enzyme commission (EC) numbers.
- Provide links to KEGG pages for the main entry and each pathway.

Return the result in a structured format: JSON or Markdown table with clear sections.
'''


def user_prompt_kegg(gene_symbol):
    return f"""
You are a bioinformatics extraction agent connected exclusively to the KEGG MCP server.
Your task is to retrieve all relevant KEGG data for a given human gene or protein.

Use only these tools:
- search_genes
- get_gene_info
- find_related_entries
- get_pathway_info
- get_disease_info
- get_drug_info
- get_module_info
- get_ko_info
- get_gene_orthologs

All information must come directly from KEGG endpoints.

---

### INPUT
Gene symbol: {gene_symbol}
Species: Homo sapiens

---

### TASKS

1. **Locate KEGG gene entry**
   - Use `search_genes` with the symbol and organism.
   - Extract: KEGG ID (e.g. "hsa:348"), gene name, KO (K-number), genomic position, strand, start, end.

2. **Retrieve detailed gene info**
   - Use `get_gene_info` and, if available, `get_ko_info` for functional class.
   - From `get_gene_info`, extract genomic location and parse to:
     position_text (e.g., "chr19:44905754..44909395"), strand, start, end.
   - Add a concise summary of the protein’s main function from KEGG descriptions.

3. **Find all directly related KEGG entities**
   - Use `find_related_entries` to discover:
     - Pathways (`path:...`)
     - Diseases (`ds:...` or `Hxxxxx`)
     - Drugs (`dr:Dxxxxx`)
     - Modules (`md:Mxxxxx`)
   - For each entity, call the corresponding `get_*_info` tool to extract summary data.
   - Include all relevant entities (not just the first).
   - For each section:
     • **Pathways:** add ID, title, description, KEGG map URL, image URL, and a note summarizing the gene’s functional role.  
     • **Diseases:** include name, short summary, BRITE class (if any), KEGG link, and a note connecting APOE to the disease mechanism.  
     • **Drugs:** include pharmacological class, structure image, target flag, and related pathways.  
     • **Modules:** include definition, functional class, and KEGG link.
   - In “notes”, highlight any relationships to longevity, aging, oxidative stress, inflammation, FOXO, mTOR, AMPK, SIRT, or autophagy.

4. **Retrieve orthology information via `get_gene_orthologs`.**
    - Call exactly: {{"gene_id":"<hsa_id>","target_organisms":["Homo sapiens"]}}
    - STRICT: Do NOT include "target_organisms" (invalid).
    - Return ≤10 orthologs (highest identity/SW score). If available, also include human paralogs from SSDB result.
    - Extract top ≤3 paralogs (within Homo sapiens) if available.
    - Include identity %, overlap, SW score, and KEGG entry URLs.
    - If available, include dendrogram URL from SSDB.
    - example: get_gene_orthologs {{"gene_id":"hsa:348","species":["Homo sapiens"]}}

5. **Return results as structured JSON**  
   Include only KEGG-derived data in this structure.
OUTPUT SCHEMA:
{{
  "query": "{{gene_symbol}}",
  "kegg": {{
    "entry": {{
      "hsa_id": "hsa:NNNN",
      "symbol": "<symbol>",
      "name": "<full gene name>",
      "ko": "<Kxxxxx>",
      "organism": "Homo sapiens",
      "position_text": "chr:start..end",
      "strand": "+|-",
      "start": <int>,
      "end": <int>,
      "notes": <text>
    }},
    "pathways": [
      {{
        "map_id": "hsaXXXXX",
        "title": "<pathway title>",
        "map_url": "https://www.kegg.jp/pathway/hsaXXXXX",
        "image_url": "https://www.kegg.jp/kegg/pathway/mapXXXXX.png",
        "notes": "<brief description of the gene's role>"
      }}
    ],
    "diseases": [
      {{
        "entry_id": "HNNNNN",
        "name": "<disease name>",
        "description": "<summary>",
        "brite": ["<classification>"],
        "urls": ["https://www.kegg.jp/entry/HNNNNN"],
        "notes": <text>
      }}
    ],
    "drugs": [
      {{
        "entry_id": "Dxxxxx",
        "name": "<drug name>",
        "class": ["<pharmacological class>"],
        "efficacy": "<short text>",
        "targets": [{{"gene": "hsa:NNNN", "symbol": "<...>", "ko": "<Kxxxxx>"}}],
        "pathways": ["hsaXXXXX"],
        "structure_image_url": "https://www.kegg.jp/ligand/Dxxxxx",
        "is_target_of_gene": <true|false>,
        "notes": <text>
      }}
    ],
    "modules": [
      {{
        "entry_id": "Mxxxxx",
        "name": "<module name>",
        "definition": "<summary>",
        "class": "<functional class>",
        "urls": ["https://www.kegg.jp/module/Mxxxxx"]
      }}
    ],
    "ssdb": {{
      "orthologs_top10": [
        {{
          "species_entry": "<org:gene_id>",
          "ko": "<Kxxxxx>",
          "identity": <float>,
          "overlap": <int>,
          "entry_url": "https://..."
        }}
      ],
      "paralogs": [
        {{
          "hsa_entry": "hsa:NNNN",
          "ko": "<Kxxxxx>",
          "identity": <float>,
          "overlap": <int>,
          "entry_url": "https://..."
        }}
      ]
    }},
    "sources": ["https://www.kegg.jp/entry/<hsa_id>"]
  }}
}}

---

### VALIDATION RULES BEFORE RETURNING
Before returning JSON, VERIFY:
- entry.position_text/strand/start/end are NOT null.
- If `find_related_entries` returns any items, ensure corresponding sections (pathways, diseases, drugs, modules) are populated.
- Each section should include at least one valid KEGG URL.
- Sources must include the main entry and all included pathway/disease/module URLs.
- Notes fields must summarize the biological or functional relevance.
- If any section expected from `find_related_entries` is empty, retry that tool once and rebuild JSON.

---

### OUTPUT FORMAT
Return only the final JSON object as described in the OUTPUT SCHEMA section (no prose, no Markdown formatting).
"""


def run_query(
    gene
):
    with ToolCollection.from_mcp(
        server_parameters=set_server(),
        trust_remote_code=True,
        structured_output=False
    ) as tools:
        agent = ToolCallingAgent(
            model=set_model(),
            tools=[*tools.tools],
            add_base_tools=False,
            max_steps=10,
        )
        agent.prompt_templates["system_prompt"] = SYSTEM_PROMPT
        return agent.run(user_prompt_kegg(gene))