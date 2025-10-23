from smolagents import ToolCollection, ToolCallingAgent, OpenAIServerModel
from mcp import StdioServerParameters
import os
import json


# config
def set_model(
    api_key=os.environ["NEBIUS_API_KEY"],
    api_base="https://api.studio.nebius.com/v1/",
    temperature=0,
    model_name="Qwen/Qwen3-235B-A22B-Thinking-2507"
):
    model = OpenAIServerModel(
        model_id=model_name,
        api_key=api_key,
        api_base=api_base,
        temperature=temperature,
    )
    return model

def set_user_prompt(uniprot_output, kegg_output, opengenes_output, gnomad_output, ncbi_output):
    return f"""
You are a bioinformatics summarization agent specialized in the **Longevity Sequence-to-Function Knowledge Base**.
You will receive as input structured JSON outputs from next data sources:
- **UniProt MCP output** (protein sequence, domains, motifs, variants, PTMs)
- **KEGG MCP output** (pathways, molecular functions, regulatory networks)
- **OpenGenes MCP output** (longevity associations, interventions, model organism data)
- **gnomAD MCP output** (pathogenic and likely pathogenic gene variants with functional impact)

---

### 🎯 TASK
Integrate and summarize the information into a **single, human-readable scientific article in Markdown (.md)** format, following the structure below.
Include insights from gnomAD regarding clinically significant variants and their potential effects on protein structure and function.

Each section should include concise yet informative text suitable for a WikiCrow-style gene/protein entry.
Where available, include UniProt, KEGG, and OpenGenes IDs and URLs.
If any data source is missing, gracefully skip the section without placeholders.

---

## 🧬 1. Gene / Protein Overview
- **Gene Symbol / Name:** from UniProt or KEGG
- **Protein Name:** official name (UniProt)
- **Identifiers:** UniProt ID, KEGG ID, Gene ID, HGNC ID, Ensembl ID (if available)
- **Organism:** Homo sapiens (unless otherwise specified)
- **Sequence Links:**  
  - [Protein (UniProt)](link)  
  - [DNA / mRNA (RefSeq or Ensembl)](link)

---

## 🔬 2. Structure and Functional Domains
- **Protein Length:** (e.g., 605 amino acids)
- **Key Domains / Motifs:** (e.g., Neh1–Neh7 domains, bZIP region, ETGE/DLG motifs)
- **Functional Roles:** summarized from UniProt and KEGG functional annotations
- **Post-Translational Modifications (PTMs):** phosphorylation, ubiquitination, etc.
- **Orthologs / Paralogs:** from KEGG or UniProt cross-refs; include species and % identity

---

## ⚙️ 3. Sequence-to-Function Relationships
| Interval | Type of Modification | Experimental Effect | Functional Outcome | Source |
|-----------|---------------------|---------------------|--------------------|--------|
| 16–32     | ETGE motif mutation | KEAP1 binding loss  | Constitutive NRF2 activation | UniProt |
| 525–550   | Neh1 domain deletion | Loss of DNA binding | Reduced antioxidant response | Literature |

- Use data from UniProt and KEGG to describe regions where amino acid changes or truncations alter protein function.
- Highlight experimentally confirmed relationships (e.g., domain deletions, point mutations, or chimeric constructs).

### 🧬 Clinically Significant Variants (gnomAD / ClinVar)
Use **gnomAD** data to summarize variants classified as *Pathogenic*, *Likely pathogenic*, or *Pathogenic/Likely pathogenic* according to ClinVar.
For each variant, include:
* **Variant ID / genomic position**
* **Amino acid change (if applicable)**
* **ClinVar significance**
* **Predicted or reported functional impact**
* **Source URL**

| Variant ID | Nucleotide / Protein Change | ClinVar Significance | Functional Impact                                | Source        |
| ---------- | --------------------------- | -------------------- | ------------------------------------------------ | ------------- |
| rs#######  | p.Arg234Trp                 | Pathogenic           | Disrupts active site, loss of enzymatic activity | [gnomAD link] |

If no qualifying variants are found, state:
> “No pathogenic or likely pathogenic variants reported in gnomAD v4.1.0 for this gene.”

---

## 🧠 4. Pathways and Functional Networks
- Extract from KEGG:
  - Pathways the protein is involved in (e.g., oxidative stress response, metabolism, reprogramming)
  - Interaction partners (if listed)
- Provide KEGG pathway map links and summarize biological roles.

---

## 🧓 5. Longevity and Aging Associations
From **OpenGenes** (and KEGG if relevant):
- Known longevity associations (pro- or anti-longevity)
- Key experiments in model organisms (C. elegans, Drosophila, mice, etc.)
- Human genetic or population associations (e.g., APOE2, FOXO3 variants)
- Known interventions (overexpression, knockdown, CRISPR, pharmacological)

Example table:

| Model | Intervention | Result | Reference |
|--------|--------------|--------|------------|
| C. elegans (skn-1) | Overexpression | ↑ Lifespan + oxidative stress resistance | PMID: 28612944 |
| Mouse (Nrf2 knockout) | Loss of function | ↓ Lifespan, ↑ inflammation | PMID: ... |

---

## 💊 6. Small Molecule and Drug Interactions
From KEGG or UniProt:
- Known small-molecule modulators, inducers, inhibitors.
- Mechanisms (binding, phosphorylation, inhibition of degradation, etc.)
- Example: *Sulforaphane* → disrupts KEAP1-NRF2 binding → activates antioxidant response.

---

## 🌍 7. Evolutionary Conservation
- Conservation of sequence motifs and domains across species.
- Note orthologs (e.g., SKN-1 in *C. elegans*, CncC in *Drosophila*).
- Discuss conservation of longevity-related functions.

---

## 📚 8. References
List all provided reference links and IDs from the source data (PMIDs, DOIs, KEGG URLs, UniProt links, OpenGenes pages, gnomAD variant URLs).

---

### OUTPUT REQUIREMENTS
- Format: **Markdown (.md)**, structured exactly as above.
- Tone: neutral, scientific, Wikipedia-style.
- Include inline citations or links to source databases whenever possible.
- Avoid speculation or unverified claims.

---

### INPUT
UniProt data:
{uniprot_output}

KEGG data:
{kegg_output}

OpenGenes data:
{opengenes_output}

gnomAD data:
{gnomad_output}

NCBI_MCP data:
{ncbi_output}

---

### OUTPUT
Return only the final Markdown article.
"""

def run_query(
    uniprot_output, kegg_output, opengenes_output, gnomad_output, ncbi_output
):
    agent = ToolCallingAgent(
        model=set_model(),
        tools=[],
        add_base_tools=False,
        max_steps=10,
    )
    # agent.prompt_templates["system_prompt"] = SYSTEM_PROMPT
    return agent.run(set_user_prompt(uniprot_output, kegg_output, opengenes_output, gnomad_output, ncbi_output))
