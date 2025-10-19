Extract knowledge from all publicly available sources regarding protein sequence-to-function relationships to empower future protein and gene reengineering efforts against aging.

## > THE_PROBLEM

Given a human protein X — how do we extract knowledge from all publicly available sources regarding its **sequence-to-function relationship** to empower future protein and gene reengineering efforts?

Protein reengineering efforts are often bottlenecked by **lack of sufficient sequence-to-function data** that would inform first rounds of designs. This challenge aims to create a comprehensive knowledge base of known protein modifications linked to functional outcomes in experiments.

## > CHALLENGE_OVERVIEW

### MISSION AND GOALS

The mission is to **speed up research on protein engineering**, especially in the context of aging. The aggregated data will help researchers identify the most promising approaches to modifying wild-type protein sequences.

Essentially, an agent is expected to reproduce a [GenAge](https://genomics.senescence.info/genes/human.html) type database but writing actual articles about the protein/gene sequence-to-function relationships related to longevity.

## > SYSTEM_REQUIREMENTS

### 1. USE WIKICROW AS REFERENCE

For starters, you can use [WikiCrow by FutureHouse](https://wikicrow.ai/APOE) as a reference format (Wikipedia-style articles about genes, e.g. APOE).

### 2. MAPPING PROTEIN/GENE SEQUENCE TO FUNCTION

This is the key requirement! The system must establish clear relationships between protein/gene sequences and their functional outcomes related to longevity.

### 3. COMPREHENSIVE ARTICLES

Write articles about protein/gene sequence-to-function relationships related to longevity. Include information about:

• Evolutionary conservation
• Orthologs/paralogs across species
• Known genetic interventions
• Mutant strains data

### 😍 BONUS FEATURES

• **Small molecule binding data** — integrate binding information for additional context
• **Tunable coarse-graining** — from individual nucleotides/amino acids to larger domains or even families of domains

## > EVALUATION_FRAMEWORK

### Breadth of Coverage (25%)
> Can your approach be applied to any human gene?

### Depth of Evidence (25%)
> Can your approach recover at least 5 various sources of modifications for each gene?

### Relation to Aging (30%)
> Is your source of protein sequence modification data relevant to aging? Is there association with lifespan?

### Source Citations (20%)
> Bonus points if agent extracts original figures with key data from source studies and cites them in the article.

## > REQUIRED_OUTPUT

### DATA STRUCTURE

- Gene/Protein Name/ID <> 
- Protein/DNA Sequence <> 
- Interval in Sequence <> 
- Function (text format)

#### PROTEIN IDENTIFIER
> Use standard protein name and/or Uniprot ID linked to a protein sequence

#### ANNOTATIONS TABLE
> Specify intervals in the protein sequence & introduced modifications and the change in function the modifications induced

## > TEST_CASES_&_VALIDATION

Test your agent with these specific proteins to validate its capability to extract comprehensive sequence-to-function relationships:

### TEST CASE 1: NRF2
Your agent should be able to find:
- Neoaves have a **KEAP1 mutation** that leads to over-active NRF2 ([PMC7234996](https://pmc.ncbi.nlm.nih.gov/articles/PMC7234996/))
- **SKN-1** (nematode's ortholog of NRF2) increases lifespan in C.elegans ([PMID: 28612944](https://pubmed.ncbi.nlm.nih.gov/28612944/))

### TEST CASE 2: SOX2
Should be able to recover the results of SuperSOX:
- [SuperSOX study](https://www.sciencedirect.com/science/article/pii/S1934590923004022) — Modified SOX2 with enhanced reprogramming capabilities

### TEST CASE 3: APOE
Should recover all major APOE variants and their longevity associations:
- **APOE2** — protective variant associated with longevity
- **APOE3** — common neutral variant
- **APOE4** — risk variant for Alzheimer's and reduced longevity

### TEST CASE 4: OCT4
Should recover papers converting OCT6 into a reprogramming factor:
- •[EMBR study](https://www.embopress.org/doi/full/10.15252/embr.201642958) — Converting OCT6 into reprogramming factor through sequence modifications

## > TECHNICAL_SPECIFICATIONS

### KNOWLEDGE BASE STRUCTURE

Gene/Protein Name/ID
    ↓
Protein/DNA Sequence
    ↓
Interval in Sequence
    ↓
Function (Text Format)
    ↓
Modification Effects
    ↓
Longevity Association

The desired structure should enable researchers to quickly identify sequence intervals of interest, understand their functional roles, and see how modifications in those regions affect longevity-related outcomes.

## > RESOURCES_&_GUIDELINES

### USEFUL DATABASES & TOOLS

#### LITERATURE & ARCHIVES
- [Anna's Archive](https://annas-archive.org/)
    Scientific literature access
- [WikiCrow](https://wikicrow.ai/APOE)
    Wikipedia-style gene articles (example: APOE)

#### PROTEIN DATABASES
- [UniProt](https://www.uniprot.org/)
    Comprehensive protein sequence and annotation database
- [AlphaFold Database](https://alphafold.ebi.ac.uk/)
    Protein structure predictions
- [InterPro](https://www.ebi.ac.uk/interpro/)
    Protein families, domains and functional sites

#### LONGEVITY DATABASES
- [GenAge](https://genomics.senescence.info/genes/index.html)
    Database of aging-related genes
- [Open Genes](https://open-genes.com/)
    Longevity-associated genes database

#### FUNCTIONAL ELEMENTS
- [ELM](http://elm.eu.org/)
    Eukaryotic Linear Motif resource

## > EXPECTED_IMPACT

Having a clear knowledge base of known protein modifications linked to functional outcomes in experiments is going to **speed up research on protein engineering**, especially in the context of aging.

#### IMMEDIATE BENEFITS

- Faster protein engineering iterations
- Informed design decisions from day one
- Reduced experimental failures
- Better starting points for modifications
#### LONG-TERM IMPACT

- Accelerated anti-aging interventions
- Cross-species insights integration
- Democratized access to expertise
- Foundation for AI-driven design