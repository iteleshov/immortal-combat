import os
from smolagents import ToolCallingAgent, ToolCollection
from smolagents.models import OpenAIServerModel
from mcp import StdioServerParameters
import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import time
import re
from typing import Set

def set_system_prompt(protein: str) -> str:
    return """
## 🔧 AGGRESSIVE NCBI EXTRACTION PROTOCOL

# 🧬 COMPREHENSIVE GENE/PROTEIN EXTRACTION: {protein.upper()}
## 🎯 MISSION: EXTRACT COMPLETE STRUCTURAL DATA WITH ALL FEATURES

## 🛠️ AVAILABLE NCBI TOOLS & PARAMETERS:

### 1. `search_ncbi` - DATABASE SEARCH
```python
search_ncbi(
    database: str,           # 'gene', 'protein', 'pubmed', 'nuccore', 'nucleotide'
    query: str,              # Search query with filters
    max_results: int = 20,   # Keep small: 3-5 for efficiency
    start_index: int = 0,    # Usually 0
    sort_order: str = ""     # MUST BE EMPTY STRING, not None! Use "" or "relevance"
)
2. fetch_records - GET FULL RECORDS
python
fetch_records(
    database: str,           # 'nuccore', 'protein', 'pubmed'
    ids: List[str],          # Array of IDs: ['NM_003106'], ['NP_003107']
    return_type: str = "gb", # "gb" (GenBank), "fasta", "xml"
    return_mode: str = "text" # "text", "xml"
)
3. summarize_records - GET METADATA SUMMARIES
python
summarize_records(
    database: str,           # 'gene', 'protein', 'pubmed'  
    ids: List[str]           # Array of IDs: ['6657'], ['NP_003107']
)
4. find_related_records - FIND CROSS-DATABASE LINKS
python
find_related_records(
    source_database: str,    # 'gene', 'protein'
    target_database: str,    # 'protein', 'nuccore', 'pubmed'
    ids: List[str]           # Array of source IDs: ['6657']
)
5. list_databases - GET AVAILABLE DATABASES
python
list_databases()  # No parameters
6. get_database_info - DATABASE METADATA
python
get_database_info(database: str = "")  # Optional database name
7. blast_search - SEQUENCE SIMILARITY
python
blast_search(
    program: str,            # 'blastn', 'blastp', 'blastx', 'tblastn', 'tblastx'
    database: str,           # 'nr', 'nt', 'refseq_protein', 'refseq_rna'
    sequence: str,           # DNA or protein sequence
    expect_value: float = 10.0,
    word_size: int = None,   # Optional
    matrix: str = None,      # Optional, e.g., 'BLOSUM62'
    gap_costs: str = None    # Optional, e.g., '11 1'
)
🎯 CRITICAL PARAMETER NOTES:
sort_order FIX:
❌ sort_order=None → CAUSES ERRORS!

✅ sort_order="" or sort_order="relevance"

Database Names:
Gene data: 'gene'

Protein sequences: 'protein'

mRNA transcripts: 'nuccore' or 'nucleotide'

Literature: 'pubmed'

Genomes: 'assembly'

Return Types for fetch_records:
GenBank features: return_type="gb"

FASTA sequences: return_type="fasta"

XML metadata: return_type="xml"

## 🎯 FOCUS: CANONICAL IDs + STRUCTURED FEATURES + RESILIENCE

### 🚀 CRITICAL MISSION: Extract complete gene/protein data with features

### 🛡️ ERROR RESILIENCE PROTOCOL:
**ON SERVER ERRORS:**
- WAIT 3-5 seconds → retry with SIMPLER query
- REMOVE complex filters → use basic search  
- TRY ALTERNATIVE DATABASE (gene → protein → nuccore)
- BROADEN SEARCH TERMS (specific → general)

**ON RATE LIMIT (429):**
- STOP IMMEDIATELY → wait 10+ seconds
- REDUCE batch size: max_results=5 → max_results=2
- FOCUS on critical data first

🛡️ CONTEXT MANAGEMENT:
TOKEN CONSERVATION:
Process ONE record at a time → extract → discard raw data

Keep ONLY structured JSON in memory

Limit feature details to essential fields

Batch similar operations

IF CONTEXT NEARS LIMIT:
SUMMARIZE progress immediately

DROP low-priority data

FOCUS on completing critical path
}
🚨 ERROR HANDLING:
SPECIFIC ERRORS:
not_found_human: No Homo sapiens gene found → return candidates

primary_assembly_not_found: No Primary Assembly block → try alternatives

incomplete_record: Missing transcripts/proteins → return partial data

blocked_or_captcha: Access blocked → return progress with URLs

VALIDATION CHECKS:
Verify length_bp = end - start + 1

Ensure range_hg38 matches Primary Assembly

Check for ≥1 transcript and ≥1 protein

Validate all sequences: no spaces, uppercase

💪 RESILIENCE MANTRA:
"EACH FAILURE IS DATA. EACH ERROR IS LEARNING. NEVER STOP TRYING DIFFERENT APPROACHES. COMPLETE DATA BEATS PERFECT DATA."

FAIL FORWARD. EXTRACT VALUE FROM EVERY ATTEMPT. THE MISSION CONTINUES.
"""

def set_user_prompt_simple_gene_id(data: dict) -> str:
    return f"""
STRICT OUTPUT FORMAT:

Find gene ID for: {data["gene_name"]}

Return ONLY JSON:
{'''{
  "gene_id": "number",
  "gene_symbol": "string"
}'''}

RULES:
- Human genes only
- No other text, only JSON
"""

def set_user_prompt_pubmed_analysis(data: dict) -> str:
    return f"""
GENE ANALYSIS FOR AGING KNOWLEDGE BASE - PubMed SEARCH

GENE INFORMATION:
{data["gene_info"]}

TASK:
Using the structural gene information above, search PubMed for relevant articles and analyze abstracts to extract data about:

1. SPECIFIC SEQUENCE MODIFICATIONS (mutations, substitutions, deletions in domains)
2. FUNCTIONAL CHANGES from these modifications  
3. AGING/LONGEVITY ASSOCIATIONS

SEARCH INSTRUCTIONS:
- Use domains and functional sites from gene information for targeted queries
- Search for specific terms: "engineered", "mutant", "mutation", "variant", "phosphorylation", "methylation"
- Combine with aging terms: "aging", "longevity", "lifespan", "senescence", "reprogramming"
- Analyze abstracts for experimental data

STRICT ANTI-HALLUCINATION RULES:
- ONLY report information explicitly stated in PubMed abstracts
- NEVER invent or assume modification details not clearly mentioned
- If abstract doesn't specify exact mutations/positions, state "Not specified in abstract"
- Only include articles with concrete experimental evidence in abstracts
- Skip articles with vague or general statements about the gene
- EVERY claim must be directly sourced to specific PMID

OUTPUT FORMAT:

=== PUBMED SEARCH RESULTS ===

[For each found article]
PMID: [number] - [Article Title]
- Found modifications: [specific substitutions/mutations] [SOURCE: PMID]
- Functional changes: [what changed] [SOURCE: PMID] 
- Aging association: [how related to aging] [SOURCE: PMID]
- Evidence level: [High/Medium/Low] [based on concrete data in abstract]

=== SUMMARY TABLE ===
| Domain/Interval | Modification Type | Effect | Aging | Source PMID |
|-----------------|-------------------|---------|--------|-------------|
| [domain/position] | [specific change] | [measured effect] | [aging link] | [PMID] |

=== ENGINEERING INSIGHTS ===
[Briefly: most promising protein modification directions with PMID references]

EXAMPLE FORMAT:
- "HMG-box domain mutations E53Q and W78R increase DNA-binding affinity [SOURCE: PMID35051363]"
- "Phosphorylation site S251A mutation reduces stem cell self-renewal in aged tissue [SOURCE: PMID28612944]"

ADDITIONAL RULES:
- Work ONLY with abstract data
- If abstract lacks modification specifics - exclude from table
- Priority to articles with experimental data
- Focus on human genes and aging
- Be precise and factual - no speculation
- Every data point must have explicit PMID citation
- Use exact wording from abstracts when possible
"""

def set_aggressive_search_prompt(data: dict) -> str:
    return f"""
ADAPTIVE AGGRESSIVE PUBMED SEARCH FOR PROTEIN ENGINEERING

GENE INFORMATION:
{data["gene_info"]}

ALREADY FOUND ARTICLES (EXCLUDE THESE):
{data["found_articles"]}

CRITICAL SEARCH STRATEGY INSTRUCTIONS:

ADAPTIVE AGGRESSION PROTOCOL:
The MORE articles we have already found, and the FEWER new results you get initially, the MORE AGGRESSIVE and CREATIVE you must become in your search strategy.

AGGRESSION SCALE:
- If finding FEW new articles (<3): Use MAXIMUM CREATIVITY and BROADEST queries
- If finding SOME articles (3-5): Use MODERATE CREATIVITY with targeted expansion  
- If finding MANY articles (>5): Use STANDARD targeted approach

CREATIVITY ESCALATION PATH:
1. FIRST: Standard structural-based queries (domains, modifications, aging)
2. THEN: Expand to RELATED biological processes and pathways
3. THEN: Explore EVOLUTIONARY and COMPARATIVE approaches
4. THEN: Use CONCEPTUAL and MECHANISTIC analogies
5. FINALLY: Try UNCONVENTIONAL but biologically plausible angles

MAXIMUM CREATIVITY MODE TRIGGERS:
- After 2+ search iterations with diminishing returns
- When standard queries yield <2 relevant articles
- When we need to uncover novel/emerging research directions

CREATIVE SEARCH ANGLES (use when needed):
- "Protein dynamics AND cellular aging AND {data["gene_name"]}"
- "Evolutionary conservation AND longevity pathways AND {data["gene_name"]}"  
- "Structural plasticity AND age-related diseases AND {data["gene_name"]}"
- "Metabolic regulation AND stem cell aging AND {data["gene_name"]}"
- "Epigenetic memory AND rejuvenation mechanisms AND {data["gene_name"]}"
- "Network analysis AND aging biomarkers AND {data["gene_name"]}"
- "Cross-species comparison AND {data["gene_name"]} longevity"
- "Protein-protein interactions AND aging networks AND {data["gene_name"]}"

TASK:
Find NEW articles not in the excluded list. Be progressively MORE CREATIVE if initial searches yield few results.

DATA EXTRACTION FOCUS:
1. SPECIFIC SEQUENCE MODIFICATIONS (mutations, substitutions, deletions in domains)
2. FUNCTIONAL CHANGES from these modifications  
3. AGING/LONGEVITY ASSOCIATIONS

RELEVANCE FILTERING:
Even in aggressive mode, MAINTAIN STRICT RELEVANCE:
- Must connect to protein sequence, structure, or function
- Must have plausible link to aging/longevity mechanisms
- Prefer articles with experimental data over theoretical

STRICT ANTI-HALLUCINATION RULES:
- ONLY report information explicitly stated in PubMed abstracts
- NEVER invent or assume modification details
- EVERY claim must be directly sourced to specific PMID

OUTPUT FORMAT:

=== NEW PUBMED SEARCH RESULTS ===

[For each NEW article found]
PMID: [number] - [Article Title]
- Found modifications: [specific substitutions/mutations] [SOURCE: PMID]
- Functional changes: [what changed] [SOURCE: PMID] 
- Aging association: [how related to aging] [SOURCE: PMID]
- Evidence level: [High/Medium/Low]
- Search aggression: [Standard / Creative / Highly Creative]

=== NEW DATA SUMMARY TABLE ===
| Domain/Interval | Modification Type | Effect | Aging | Source PMID |

=== AGGRESSION STRATEGY REPORT ===
- Initial results: [number found with standard approach]
- Creative escalation: [Yes/No and which creative approaches used]
- Final article count: [total new relevant articles]
- Recommendation: [Continue aggressive search / Sufficient coverage / Switch genes]

FINAL DIRECTIVE:
DO NOT stop searching until you have exhausted creative approaches or found sufficient new data. The goal is MAXIMUM COVERAGE of relevant literature.
"""

def set_extraction_prompt(search_results_text: str) -> str:
    return f"""
    EXTRACT ONLY PMID AND TITLE LINES FROM SEARCH RESULTS

    SEARCH RESULTS TEXT:
    {search_results_text}

    TASK:
    Extract ONLY the lines that contain "PMID: [number] - [Article Title]". Ignore everything else.

    RULES:
    1. Extract ONLY lines that match pattern "PMID: [digits] - [text]"
    2. Skip all analysis, summaries, tables, and other text
    3. Preserve exact wording including punctuation
    4. Remove duplicate lines if same PMID appears multiple times
    5. Return each matching line on a separate line

    OUTPUT FORMAT:
    Return ONLY the extracted lines, one per line. No other text.

    EXAMPLES:
    Input: "PMID: 28059768 - SOX2 promotes lineage plasticity and antiandrogen resistance in TP53- and RB1-deficient prostate cancer."
    Output: "PMID: 28059768 - SOX2 promotes lineage plasticity and antiandrogen resistance in TP53- and RB1-deficient prostate cancer."

    Input: "Some analysis text... PMID: 33268865 - Reprogramming to recover youthful epigenetic information and restore vision. More analysis..."
    Output: "PMID: 33268865 - Reprogramming to recover youthful epigenetic information and restore vision."

    EXTRACT NOW:
    """

def set_cleanup_results_prompt(accumulated_results: str) -> str:
    return f"""
    CLEAN AND STRUCTURE ACCUMULATED SEARCH RESULTS

    ACCUMULATED RESULTS:
    {accumulated_results}

    TASK:
    Clean, deduplicate, and structure all the accumulated PubMed search results into a clear, readable format.

    CRITICAL RULES:
    1. REMOVE ALL duplicates - keep only one entry per PMID
    2. PRESERVE ALL original information - do not remove any relevant data
    3. REMOVE non-relevant sections like search strategy reports, error messages, technical notes
    4. KEEP ALL article data including modifications, functional changes, aging associations
    5. ORGANIZE in logical sections
    6. DO NOT invent, modify, or hallucinate any information
    7. USE exact wording from the original text

    CLEANING INSTRUCTIONS:
    - Remove duplicate articles (same PMID)
    - Remove "AGGRESSION STRATEGY REPORT" sections  
    - Remove "SEARCH STRATEGY REPORT" sections
    - Remove error messages and technical notes
    - Remove empty or irrelevant tables
    - Keep ALL article data and summaries

    ORGANIZATION FORMAT:
    Structure the cleaned results as follows:

    === CLEANED PUBMED RESULTS ===

    [RELEVANT ARTICLES WITH EXPERIMENTAL DATA]
    PMID: [number] - [Title]
    - Found modifications: [extract ALL modification data]
    - Functional changes: [extract ALL functional data]
    - Aging association: [extract ALL aging data]
    - Evidence level: [keep original assessment]

    [ARTICLES WITH INDIRECT/MECHANISTIC RELEVANCE]
    PMID: [number] - [Title] 
    - Key findings: [summarize relevant mechanistic insights]
    - Aging relevance: [explain indirect connection to aging]

    === SUMMARY OF KEY MODIFICATIONS ===
    [Extract ALL unique sequence modifications found across all articles]

    === OVERALL COVERAGE ASSESSMENT ===
    [Brief factual summary of what was found and gaps]

    PRESERVATION RULES:
    - Keep EVERY article that mentions SOX2 modifications, functions, or aging
    - Preserve EXACT wording for modifications and experimental findings
    - Include BOTH direct and indirect aging associations
    - Maintain original evidence level assessments

    DO NOT:
    - Remove any articles with actual SOX2 data
    - Change any experimental findings
    - Invent new modifications or effects
    - Combine information from different articles

    CLEAN AND ORGANIZE NOW:
    """
def run_super_agent(info: str, steps: int, user_promt_func: Any, protein: str) -> str:
    """Запуск супер-агента для хакатона с увеличенным количеством шагов"""
    try:
        with ToolCollection.from_mcp(
                server_parameters=set_server_stdio(),
                trust_remote_code=True,
                structured_output=False
        ) as tools:

            agent = ToolCallingAgent(
                model=set_model(),
                tools=[*tools.tools],
                add_base_tools=False,
                max_steps=steps,
            )
            agent.prompt_templates["system_prompt"] = set_system_prompt(protein)
            user_message = user_promt_func(info)
            result = agent.run(user_message)
        return result
    except Exception as e:
        return f"Ошибка: {e}"


def get_gene_id_simple(response: str) -> str:
    """Простой способ извлечения gene_id"""
    import re

    # Способ 1: Ищем любой числовой ID после "ids"
    match = re.search(r'"ids"\s*[|:]\s*.*?"(\d+)"', response)
    if match:
        return match.group(1)

    # Способ 2: Ищем просто числовой ID в ответе
    numbers = re.findall(r'\b\d+\b', response)
    for num in numbers:
        if len(num) >= 4 and len(num) <= 10:  # gene_id обычно 4-10 цифр
            return num

    return None

def get_element_text_fixed(element: Optional[ET.Element], path: str, namespaces: Dict = None) -> str:
    """Безопасно получает текст элемента с учетом namespace"""
    if element is None:
        return ""

    if namespaces:
        target = element.find(path, namespaces)
    else:
        target = element.find(path)

    return target.text if target is not None and target.text else ""

def call_llm_directly(prompt: str) -> str:
    """Прямой вызов LLM модели для суммаризации"""
    try:
        model = OpenAIServerModel(
            model_id="Qwen/Qwen3-235B-A22B-Instruct-2507",
            api_key=os.environ["NEBIUS_API_KEY"],
            api_base="https://api.studio.nebius.com/v1/",
            temperature=0.1
        )

        messages = [{"role": "user", "content": prompt}]
        response = model(messages)
        return response
    except Exception as e:
        return f"Ошибка LLM: {e}"

def parse_protein_all_fields(protein_accession: str) -> Dict[str, Any]:
    """
    ИЗВЛЕКАЕТ ДАННЫЕ ИЗ ВСЕХ ПОЛЕЙ БЕЛКА В СЛОВАРЬ
    """
    try:
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {
            'db': 'protein',
            'id': protein_accession,
            'rettype': 'gb',
            'retmode': 'text'
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        protein_data = {}
        lines = response.text.split('\n')
        current_field = None
        field_content = []

        for line in lines:
            line = line.rstrip()

            if line and line[0].isupper() and not line.startswith(' '):
                if current_field and field_content:
                    protein_data[current_field] = '\n'.join(field_content).strip()

                current_field = line.split()[0] if line.split() else None
                field_content = [line[12:].strip()] if len(line) > 12 else [line]

            elif current_field and line.startswith(' '):
                field_content.append(line.strip())

        if current_field and field_content:
            protein_data[current_field] = '\n'.join(field_content).strip()

        return protein_data

    except Exception as e:
        return {'error': f'Ошибка: {str(e)}'}

def extract_protein_features(features_text: str) -> Dict[str, Any]:
    """
    Парсит раздел FEATURES белка - самый важный для хакатона!
    """
    features_data = {
        'domains': [],
        'sites': [],
        'regions': [],
        'modifications': []
    }

    lines = features_text.split('\n')
    current_feature = None
    current_content = []

    for line in lines:
        line = line.strip()
        if line and not line.startswith('/'):
            if current_feature and current_content:
                save_protein_feature(current_feature, current_content, features_data)

            parts = line.split()
            if parts:
                current_feature = parts[0]
                current_content = [line]
        elif line.startswith('/'):
            current_content.append(line)

    if current_feature and current_content:
        save_protein_feature(current_feature, current_content, features_data)

    return features_data

def save_protein_feature(feature_type: str, content: List[str], features_data: Dict[str, Any]):
    """Сохраняет информацию о фиче в структурированном виде"""
    feature_text = ' '.join(content)

    if feature_type == 'Region':
        features_data['domains'].append({
            'type': 'domain',
            'description': feature_text,
            'location': extract_location_from_feature(feature_text)
        })
    elif feature_type == 'Site':
        features_data['sites'].append({
            'type': 'site',
            'description': feature_text,
            'location': extract_location_from_feature(feature_text)
        })
    elif 'binding' in feature_text.lower():
        features_data['sites'].append({
            'type': 'binding_site',
            'description': feature_text,
            'location': extract_location_from_feature(feature_text)
        })
    elif any(mod in feature_text.lower() for mod in ['phospho', 'acetyl', 'methyl']):
        features_data['modifications'].append({
            'type': 'ptm',
            'description': feature_text,
            'location': extract_location_from_feature(feature_text)
        })

def extract_location_from_feature(feature_text: str) -> str:
    """Извлекает локализацию из текста фичи"""
    import re
    match = re.search(r'(\d+\.\.\d+)', feature_text)
    return match.group(1) if match else ""

def extract_protein_references(references_text: str) -> List[Dict[str, str]]:
    """Извлекает информацию о ссылках"""
    references = []
    lines = references_text.split('\n')
    current_ref = {}

    for line in lines:
        line = line.strip()
        if line.startswith('REFERENCE'):
            if current_ref:
                references.append(current_ref)
            current_ref = {}
        elif line.startswith('AUTHORS'):
            current_ref['authors'] = line.replace('AUTHORS', '').strip()
        elif line.startswith('TITLE'):
            current_ref['title'] = line.replace('TITLE', '').strip()
        elif line.startswith('JOURNAL'):
            current_ref['journal'] = line.replace('JOURNAL', '').strip()
        elif line.startswith('PUBMED'):
            current_ref['pmid'] = line.replace('PUBMED', '').strip()

    if current_ref:
        references.append(current_ref)

    return references

def summarize_ALL_fields_protein(protein_data: Dict[str, Any], llm_call=call_llm_directly, verbose: bool = False) -> Dict[str, Any]:
    """
    Суммаризация ВСЕХ полей белка с ЖЕСТКИМ запретом галлюцинаций
    """

    def log(msg: str):
        if verbose:
            print(f"🔧 {msg}")

    summaries = {}

    LIST_LENGTH_THRESHOLD = 8
    JSON_CHAR_THRESHOLD = 800
    TEXT_CHAR_THRESHOLD = 500

    def should_summarize_list(lst: List) -> bool:
        if not lst:
            return False
        if len(lst) > LIST_LENGTH_THRESHOLD:
            return True
        for item in lst:
            if isinstance(item, (dict, list)):
                if len(json.dumps(item, ensure_ascii=False)) > JSON_CHAR_THRESHOLD:
                    return True
            elif isinstance(item, str) and len(item) > TEXT_CHAR_THRESHOLD:
                return True
        return False

    def summarize_field(field_name: str, prompt_text: str, value: Any) -> str:
        """Суммаризация одного поля с жестким запретом галлюцинаций"""
        try:
            payload = json.dumps(value, ensure_ascii=False, indent=2, default=str)

            strict_prompt = (
                f"{prompt_text}\n\n"
                "STRICT RULES - DO NOT VIOLATE:\n"
                "1. NEVER add any information not present in the data\n"
                "2. NEVER make inferences or draw conclusions\n"
                "3. NEVER create new facts or connections\n"
                "4. ONLY summarize what is explicitly in the data\n"
                "5. Keep it factual and concise\n"
                "6. If data is unclear, say so - don't guess\n\n"
                f"DATA TO SUMMARIZE:\n{payload}"
            )

            response = llm_call(strict_prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            return f"Ошибка суммаризации: {str(e)}"

    log("Этап 1: Обработка основной информации о белке...")

    if 'LOCUS' in protein_data:
        summaries['basic_info'] = {
            'accession': protein_data.get('ACCESSION', ''),
            'definition': protein_data.get('DEFINITION', ''),
            'length': protein_data.get('LOCUS', ''),
            'organism': protein_data.get('SOURCE', '')
        }

    log("Этап 2: Обработка FEATURES...")

    if 'FEATURES' in protein_data:
        features_parsed = extract_protein_features(protein_data['FEATURES'])

        if features_parsed['domains']:
            if should_summarize_list(features_parsed['domains']):
                try:
                    log("  🤖 Суммаризируем домены...")
                    summaries['domains_summary'] = summarize_field(
                        'protein_domains',
                        "Summarize the protein domains FACTUALLY. List domains mentioned with their locations:",
                        features_parsed['domains']
                    )
                except Exception as e:
                    summaries['domains_error'] = str(e)
                    summaries['domains_raw'] = features_parsed['domains'][:5]
            else:
                summaries['domains'] = features_parsed['domains']

        if features_parsed['sites']:
            summaries['functional_sites'] = features_parsed['sites'][:10]

    log("Этап 3: Обработка последовательности...")

    if 'ORIGIN' in protein_data:
        seq_data = protein_data['ORIGIN']
        summaries['sequence_info'] = {
            'has_sequence': True,
            'sequence_length': len([c for c in seq_data if c.isalpha()]),
            'first_50_aa': ''.join([c for c in seq_data if c.isalpha()])[:50] + '...' if len(seq_data) > 50 else seq_data
        }

    log("Этап 4: Обработка ссылок и комментариев...")

    if 'REFERENCE' in protein_data:
        references = extract_protein_references(protein_data['REFERENCE'])
        if references and len(references) > 5:
            try:
                log("  🤖 Суммаризируем ссылки...")
                summaries['references_summary'] = summarize_field(
                    'protein_references',
                    "List the main publications FACTUALLY:",
                    [f"{ref.get('pmid', '')}: {ref.get('title', '')[:100]}..." for ref in references[:10]]
                )
            except Exception as e:
                summaries['references_error'] = str(e)
        else:
            summaries['references'] = references

    if 'COMMENT' in protein_data and len(protein_data['COMMENT']) > TEXT_CHAR_THRESHOLD:
        try:
            log("  🤖 Суммаризируем комментарий...")
            summaries['comment_summary'] = summarize_field(
                'protein_comment',
                "Summarize the protein comment information FACTUALLY:",
                protein_data['COMMENT']
            )
        except Exception as e:
            summaries['comment_error'] = str(e)

    log("Этап 5: Финальная суммаризация...")

    try:
        final_prompt_parts = []

        for key, value in summaries.items():
            if key.endswith('_error'):
                continue

            section_text = json.dumps(value, ensure_ascii=False, indent=2)
            final_prompt_parts.append(f"=== {key.upper()} ===\n{section_text}")

        final_prompt = (
                "Create a WELL-STRUCTURED summary of the PROTEIN data below.\n\n"
                "🔴 STRICT PROHIBITIONS:\n"
                "1. NEVER add information not explicitly in the data\n"
                "2. NEVER make inferences or conclusions\n"
                "3. ONLY use facts from provided data\n"
                "🟢 WHAT TO DO:\n"
                "1. Be concise but comprehensive\n"
                "2. Maintain factual accuracy\n\n"
                "PROTEIN DATA:\n" + "\n\n".join(final_prompt_parts)
        )

        log("  🤖 Вызываем финальную суммаризацию...")
        summaries['final_protein_article'] = llm_call(final_prompt)
        log("  ✅ Финальная суммаризация завершена!")

    except Exception as e:
        summaries['final_article_error'] = str(e)
        log(f"  ❌ Ошибка финальной суммаризации: {e}")

    log("Этап 6: Формирование результата...")

    result = {
        'protein_summaries': summaries,
        'sections_count': len(summaries),
        'has_domains': 'domains' in summaries or 'domains_summary' in summaries,
        'has_sequence': 'sequence_info' in summaries,
        'processing_timestamp': datetime.now().isoformat()
    }

    log(f"✅ Суммаризация белка завершена! Создано {len(summaries)} разделов")

    return result

def process_protein(protein_accession: str):
    """Полный процесс обработки белка для хакатона"""
    print(f"🔬 Обрабатываем белок: {protein_accession}")

    protein_data = parse_protein_all_fields(protein_accession)

    if 'error' in protein_data:
        print(f"❌ Ошибка: {protein_data['error']}")
        return None

    print(f"✅ Получено полей: {list(protein_data.keys())}")

    summary = summarize_ALL_fields_protein(protein_data, verbose=True)

    return summary

def get_element_attribute(element: ET.Element, tag: str, attribute: str) -> Optional[str]:
    """Вспомогательная функция для получения атрибута элемента"""
    if element is None:
        return None
    elem = element.find(tag)
    if elem is not None:
        return elem.get(attribute)
    return None

def set_server_stdio(server_name="ncbi_mcp_server"):
    return StdioServerParameters(
        command="docker",
        args=["exec", "-i", server_name, "python", "/app/ncbi_mcp_server/server.py"],
        env={
            "NCBI_API_KEY": os.environ.get("NCBI_API_KEY", ""),
            "NCBI_EMAIL": os.environ.get("NCBI_EMAIL", "")
        }
    )

def set_model():
    return OpenAIServerModel(
        model_id="Qwen/Qwen3-235B-A22B-Instruct-2507",
        api_key=os.environ["NEBIUS_API_KEY"],
        api_base="https://api.studio.nebius.com/v1/",
        temperature=0.1,
        max_tokens=4000,
    )



def extract_ALL_fields_gene(gene_id: str) -> Dict[str, Any]:
    """
    ИЗВЛЕКАЕТ ВСЕ ПОЛЯ из XML гена - ПОЛНОЕ ПОКРЫТИЕ
    Возвращает готовый словарь со всеми данными
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {'db': 'gene', 'id': gene_id, 'retmode': 'xml'}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        root = ET.fromstring(response.text)

        all_data = {}

        all_data['entrezgene'] = extract_entrezgene_info(root)
        all_data['gene_info'] = extract_gene_info(root)
        all_data['gene_commentaries'] = extract_all_gene_commentaries(root)
        all_data['biosource'] = extract_biosource_info(root)
        all_data['genomics'] = extract_genomics_info(root)
        all_data['publications'] = extract_publications_info(root)
        all_data['properties'] = extract_properties_info(root)
        all_data['technical'] = extract_technical_info(root)
        all_data['additional'] = extract_additional_sections(root)

        return all_data

    except Exception as e:
        return {'error': f'Ошибка парсинга: {str(e)}'}

def extract_entrezgene_info(root: ET.Element) -> Dict[str, Any]:
    """Извлекает основную структуру Entrezgene"""
    entrezgene_info = {}

    entrezgene = root.find('.//Entrezgene')
    if entrezgene is not None:
        entrezgene_info['type'] = entrezgene.get('type')

        unique_keys = entrezgene.find('Entrezgene_unique-keys')
        if unique_keys is not None:
            entrezgene_info['unique_keys'] = [key.text for key in unique_keys.findall('Object-id') if key.text]

        entrezgene_type = entrezgene.find('Entrezgene_type')
        if entrezgene_type is not None:
            entrezgene_info['gene_type'] = entrezgene_type.text

    return entrezgene_info

def extract_gene_info(root: ET.Element) -> Dict[str, Any]:
    """Извлекает основную информацию о гене"""
    gene_info = {}

    gene_ref = root.find('.//Gene-ref')
    if gene_ref is not None:
        gene_info['symbol'] = gene_ref.findtext('Gene-ref_locus')
        gene_info['description'] = gene_ref.findtext('Gene-ref_desc')
        gene_info['maploc'] = gene_ref.findtext('Gene-ref_maploc')
        gene_info['formal_name'] = gene_ref.findtext('Gene-ref_formal-name')
        gene_info['db'] = gene_ref.findtext('Gene-ref_db')

        synonyms = []
        for syn in gene_ref.findall('Gene-ref_syn'):
            if syn.text:
                synonyms.append(syn.text)
        gene_info['synonyms'] = synonyms

    nomenclature = root.find('.//Gene-nomenclature')
    if nomenclature is not None:
        gene_info['nomenclature'] = {
            'symbol': nomenclature.findtext('Gene-nomenclature_symbol'),
            'name': nomenclature.findtext('Gene-nomenclature_name'),
            'status': nomenclature.findtext('Gene-nomenclature_status'),
            'source': nomenclature.findtext('Gene-nomenclature_source')
        }

    summary = root.find('.//Entrezgene_summary')
    if summary is not None:
        gene_info['summary'] = summary.text

    locus = root.find('.//Entrezgene_locus')
    if locus is not None:
        gene_info['locus'] = locus.text

    prot_ref = root.find('.//Entrezgene_prot/Prot-ref')
    if prot_ref is not None:
        gene_info['protein'] = {
            'name': prot_ref.findtext('Prot-ref_name'),
            'description': prot_ref.findtext('Prot-ref_desc')
        }
        alt_names = []
        for name_elem in prot_ref.findall('Prot-ref_name_E'):
            if name_elem.text:
                alt_names.append(name_elem.text)
        if alt_names:
            gene_info['protein']['alternative_names'] = alt_names

    return gene_info

def extract_all_gene_commentaries(root: ET.Element) -> List[Dict[str, Any]]:
    """Извлекает ВСЕ Gene-commentary с полной структурой"""
    commentaries = []

    for commentary in root.findall('.//Gene-commentary'):
        comment_data = extract_gene_commentary_element(commentary)
        if comment_data:
            commentaries.append(comment_data)

    return commentaries

def extract_gene_commentary_element(commentary: ET.Element) -> Dict[str, Any]:
    """Извлекает один элемент Gene-commentary со всеми полями"""
    comment_data = {}

    comment_data['type'] = get_element_attribute(commentary, 'Gene-commentary_type', 'value')
    comment_data['heading'] = commentary.findtext('Gene-commentary_heading')
    comment_data['text'] = commentary.findtext('Gene-commentary_text')
    comment_data['label'] = commentary.findtext('Gene-commentary_label')
    comment_data['accession'] = commentary.findtext('Gene-commentary_accession')
    comment_data['version'] = commentary.findtext('Gene-commentary_version')

    comment_data['create_date'] = commentary.findtext('Gene-commentary_create-date')
    comment_data['update_date'] = commentary.findtext('Gene-commentary_update-date')

    genomic_coords = commentary.find('Gene-commentary_genomic-coords')
    if genomic_coords is not None:
        comment_data['genomic_coords'] = extract_genomic_coords(genomic_coords)

    source = commentary.find('Gene-commentary_source')
    if source is not None:
        comment_data['source'] = extract_source_info(source)

    comments = []
    for comment_elem in commentary.findall('Gene-commentary_comment/Gene-commentary'):
        nested_comment = extract_gene_commentary_element(comment_elem)
        if nested_comment:
            comments.append(nested_comment)
    if comments:
        comment_data['comments'] = comments

    products = []
    for product in commentary.findall('Gene-commentary_products/Gene-commentary'):
        product_data = extract_gene_commentary_element(product)
        if product_data:
            products.append(product_data)
    if products:
        comment_data['products'] = products

    refs = []
    for ref in commentary.findall('Gene-commentary_refs/Pub'):
        ref_data = extract_publication_info(ref)
        if ref_data:
            refs.append(ref_data)
    if refs:
        comment_data['references'] = refs

    seqs = []
    for seq in commentary.findall('Gene-commentary_seqs/Seq-loc'):
        seq_data = extract_sequence_location(seq)
        if seq_data:
            seqs.append(seq_data)
    if seqs:
        comment_data['sequences'] = seqs

    xtra_props = commentary.find('Gene-commentary_xtra-properties')
    if xtra_props is not None:
        comment_data['extra_properties'] = extract_xtra_properties(xtra_props)

    return comment_data

def extract_genomic_coords(genomic_coords_element: ET.Element) -> Dict[str, Any]:
    """Извлекает геномные координаты"""
    coords_data = {}

    seq_loc = genomic_coords_element.find('Seq-loc')
    if seq_loc is not None:
        coords_data['seq_loc'] = extract_sequence_location(seq_loc)

    return coords_data

def extract_source_info(source_element: ET.Element) -> Dict[str, Any]:
    """Извлекает информацию об источнике"""
    source_data = {}

    other_source = source_element.find('Other-source')
    if other_source is not None:
        source_data['other_source'] = {
            'anchor': other_source.findtext('Other-source_anchor'),
            'pre_text': other_source.findtext('Other-source_pre-text'),
            'post_text': other_source.findtext('Other-source_post-text'),
            'src': other_source.findtext('Other-source_src'),
            'url': other_source.findtext('Other-source_url')
        }

    return source_data

def extract_xtra_properties(xtra_props_element: ET.Element) -> List[Dict[str, str]]:
    """Извлекает дополнительные свойства"""
    properties = []

    for term in xtra_props_element.findall('Xtra-Terms'):
        tag = term.findtext('Xtra-Terms_tag')
        value = term.findtext('Xtra-Terms_value')
        if tag and value:
            properties.append({'tag': tag, 'value': value})

    return properties

def extract_biosource_info(root: ET.Element) -> Dict[str, Any]:
    """Извлекает информацию о биологическом источнике"""
    biosource = {}

    bio_source = root.find('.//BioSource')
    if bio_source is not None:
        biosource['genome'] = bio_source.findtext('BioSource_genome')
        biosource['origin'] = bio_source.findtext('BioSource_origin')

        org = bio_source.find('BioSource_org')
        if org is not None:
            biosource['organism'] = extract_organism_info(org)

        subtypes = []
        for subtype in bio_source.findall('BioSource_subtype'):
            subtype_data = {
                'name': subtype.findtext('SubSource_name'),
                'subtype': subtype.findtext('SubSource_subtype')
            }
            if subtype_data['name'] or subtype_data['subtype']:
                subtypes.append(subtype_data)
        if subtypes:
            biosource['subtypes'] = subtypes

    return biosource

def extract_organism_info(org_element: ET.Element) -> Dict[str, Any]:
    """Извлекает полную информацию об организме"""
    organism = {}

    org_ref = org_element.find('Org-ref')
    if org_ref is not None:
        organism['common_name'] = org_ref.findtext('Org-ref_common')
        organism['taxname'] = org_ref.findtext('Org-ref_taxname')
        organism['db'] = org_ref.findtext('Org-ref_db')

    org_name = org_element.find('OrgName')
    if org_name is not None:
        organism['lineage'] = org_name.findtext('OrgName_lineage')
        organism['gcode'] = org_name.findtext('OrgName_gcode')
        organism['mgcode'] = org_name.findtext('OrgName_mgcode')
        organism['div'] = org_name.findtext('OrgName_div')
        organism['attrib'] = org_name.get('attrib')

        binomial = org_name.find('OrgName_name/BinomialOrgName')
        if binomial is not None:
            organism['binomial'] = {
                'genus': binomial.findtext('BinomialOrgName_genus'),
                'species': binomial.findtext('BinomialOrgName_species')
            }

    return organism

def extract_genomics_info(root: ET.Element) -> Dict[str, Any]:
    """Извлекает геномную информацию"""
    genomics = {}

    location = root.find('.//Entrezgene_location')
    if location is not None:
        genomics['location'] = extract_location_info(location)

    maps_elem = root.find('.//Maps_display-str')
    if maps_elem is not None:
        genomics['maps_display'] = maps_elem.text

    maps_method = root.find('.//Maps_method')
    if maps_method is not None:
        genomics['maps_method'] = {
            'map_type': maps_method.findtext('Maps_method_map-type')
        }

    na_strand = root.find('.//Na-strand')
    if na_strand is not None:
        genomics['na_strand'] = na_strand.text

    return genomics

def extract_location_info(location_element: ET.Element) -> Dict[str, Any]:
    """Извлекает информацию о локализации"""
    location = {}

    seq_interval = location_element.find('.//Seq-interval')
    if seq_interval is not None:
        location['seq_interval'] = {
            'from': seq_interval.findtext('Seq-interval_from'),
            'to': seq_interval.findtext('Seq-interval_to'),
            'strand': seq_interval.findtext('Seq-interval_strand'),
            'id': extract_seq_id(seq_interval.find('Seq-interval_id'))
        }

    seq_loc = location_element.find('.//Seq-loc')
    if seq_loc is not None:
        location['seq_loc'] = extract_sequence_location(seq_loc)

    return location

def extract_sequence_location(seq_loc: ET.Element) -> Dict[str, Any]:
    """Извлекает информацию о последовательности"""
    seq_data = {}

    whole = seq_loc.find('Seq-loc_whole')
    if whole is not None:
        seq_data['whole'] = extract_seq_id(whole.find('Seq-id'))

    interval = seq_loc.find('Seq-loc_int')
    if interval is not None:
        seq_data['interval'] = extract_seq_interval(interval)

    return seq_data

def extract_seq_interval(interval_element: ET.Element) -> Dict[str, Any]:
    """Извлекает информацию об интервале последовательности"""
    interval = {}

    seq_interval = interval_element.find('Seq-interval')
    if seq_interval is not None:
        interval['from'] = seq_interval.findtext('Seq-interval_from')
        interval['to'] = seq_interval.findtext('Seq-interval_to')
        interval['strand'] = seq_interval.findtext('Seq-interval_strand')
        interval['seq_id'] = extract_seq_id(seq_interval.find('Seq-interval_id/Seq-id'))

    return interval

def extract_seq_id(seq_id_element: Optional[ET.Element]) -> Dict[str, str]:
    """Извлекает информацию о Seq-id"""
    if seq_id_element is None:
        return {}

    seq_id_data = {}
    gi = seq_id_element.findtext('Seq-id_gi')
    if gi:
        seq_id_data['gi'] = gi

    return seq_id_data

def extract_publications_info(root: ET.Element) -> List[Dict[str, Any]]:
    """Извлекает информацию о публикациях"""
    publications = []

    for pub in root.findall('.//Pub'):
        pub_data = extract_publication_info(pub)
        if pub_data:
            publications.append(pub_data)

    return publications

def extract_publication_info(pub_element: ET.Element) -> Dict[str, Any]:
    """Извлекает информацию о публикации"""
    pub_data = {}

    pub_data['pmid'] = pub_element.findtext('Pub_pmid')

    pubmed_id = pub_element.find('PubMedId')
    if pubmed_id is not None:
        pub_data['pubmed_id'] = pubmed_id.text

    return pub_data

def extract_properties_info(root: ET.Element) -> Dict[str, Any]:
    """Извлекает свойства и дополнительные данные"""
    properties = {}

    xtra_terms = []
    for term in root.findall('.//Xtra-Terms'):
        tag = term.findtext('Xtra-Terms_tag')
        value = term.findtext('Xtra-Terms_value')
        if tag and value:
            xtra_terms.append({'tag': tag, 'value': value})
    if xtra_terms:
        properties['xtra_terms'] = xtra_terms

    additional_props = []
    for prop in root.findall('.//Entrezgene_xtra-properties/Xtra-Terms'):
        tag = prop.findtext('Xtra-Terms_tag')
        value = prop.findtext('Xtra-Terms_value')
        if tag and value:
            additional_props.append({'tag': tag, 'value': value})
    if additional_props:
        properties['additional_properties'] = additional_props

    index_terms = []
    for term in root.findall('.//Entrezgene_xtra-index-terms/E'):
        if term.text:
            index_terms.append(term.text)
    if index_terms:
        properties['index_terms'] = index_terms

    return properties

def extract_technical_info(root: ET.Element) -> Dict[str, Any]:
    """Извлекает техническую информацию"""
    technical = {}

    track_info = root.find('.//Gene-track')
    if track_info is not None:
        technical['track'] = {
            'geneid': track_info.findtext('Gene-track_geneid'),
            'status': track_info.findtext('Gene-track_status'),
            'create_date': track_info.findtext('Gene-track_create-date'),
            'update_date': track_info.findtext('Gene-track_update-date')
        }

    gene_source = root.find('.//Gene-source')
    if gene_source is not None:
        technical['gene_source'] = {
            'src': gene_source.findtext('Gene-source_src'),
            'src_int': gene_source.findtext('Gene-source_src-int'),
            'src_str2': gene_source.findtext('Gene-source_src-str2')
        }

    dates = []
    for date_elem in root.findall('.//Date'):
        date_data = extract_date_info(date_elem)
        if date_data:
            dates.append(date_data)
    if dates:
        technical['dates'] = dates

    return technical

def extract_date_info(date_element: ET.Element) -> Dict[str, Any]:
    """Извлекает информацию о дате"""
    date_data = {}

    date_std = date_element.find('Date-std')
    if date_std is not None:
        date_data['std'] = {
            'year': date_std.findtext('Date-std_year'),
            'month': date_std.findtext('Date-std_month'),
            'day': date_std.findtext('Date-std_day'),
            'hour': date_std.findtext('Date-std_hour'),
            'minute': date_std.findtext('Date-std_minute'),
            'second': date_std.findtext('Date-std_second')
        }

    return date_data

def extract_additional_sections(root: ET.Element) -> Dict[str, Any]:
    """Извлекает дополнительные разделы"""
    additional = {}

    other_sources = []
    for source in root.findall('.//Other-source'):
        source_data = {
            'anchor': source.findtext('Other-source_anchor'),
            'pre_text': source.findtext('Other-source_pre-text'),
            'post_text': source.findtext('Other-source_post-text'),
            'src': source.findtext('Other-source_src'),
            'url': source.findtext('Other-source_url')
        }
        if any(source_data.values()):
            other_sources.append(source_data)
    if other_sources:
        additional['other_sources'] = other_sources

    dbtags = []
    for dbtag in root.findall('.//Dbtag'):
        db = dbtag.findtext('Dbtag_db')
        tag = dbtag.findtext('Dbtag_tag')
        if db and tag:
            dbtags.append({'db': db, 'tag': tag})
    if dbtags:
        additional['external_dbs'] = dbtags

    object_ids = []
    for obj_id in root.findall('.//Object-id'):
        obj_data = {
            'id': obj_id.findtext('Object-id_id'),
            'str': obj_id.findtext('Object-id_str')
        }
        if any(obj_data.values()):
            object_ids.append(obj_data)
    if object_ids:
        additional['object_ids'] = object_ids

    return additional

def create_extraction_summary(all_data: Dict[str, Any]) -> Dict[str, Any]:
    """Создает сводку по извлеченным данным"""
    pathways = []
    for commentary in all_data.get('gene_commentaries', []):
        if commentary.get('type') == 'pathway' or 'pathway' in str(commentary.get('heading', '')).lower():
            pathways.append(commentary)

    commentary_types = {}
    for commentary in all_data.get('gene_commentaries', []):
        c_type = commentary.get('type', 'other')
        commentary_types[c_type] = commentary_types.get(c_type, 0) + 1

    summary = {
        'total_gene_commentaries': len(all_data.get('gene_commentaries', [])),
        'commentary_types_count': commentary_types,
        'total_pathways': len(pathways),
        'total_publications': len(all_data.get('publications', [])),
        'total_external_dbs': len(all_data.get('additional', {}).get('external_dbs', [])),
        'has_genomic_data': bool(all_data.get('genomics', {}).get('location')),
        'has_protein_data': bool(all_data.get('gene_info', {}).get('protein')),
        'extraction_timestamp': datetime.now().isoformat()
    }

    return summary

def summarize_ALL_fields_gene(all_data: Dict[str, Any], llm_call=call_llm_directly, verbose: bool = False) -> Dict[str, Any]:
    """
    Суммаризация ВСЕХ полей из нового парсера с ЖЕСТКИМ запретом галлюцинаций
    """

    def log(msg: str):
        if verbose:
            print(f"🔧 {msg}")

    summaries = {}

    LIST_LENGTH_THRESHOLD = 8
    JSON_CHAR_THRESHOLD = 800
    TEXT_CHAR_THRESHOLD = 500

    def should_summarize_list(lst: List) -> bool:
        if not lst:
            return False
        if len(lst) > LIST_LENGTH_THRESHOLD:
            return True
        for item in lst:
            if isinstance(item, (dict, list)):
                if len(json.dumps(item, ensure_ascii=False)) > JSON_CHAR_THRESHOLD:
                    return True
            elif isinstance(item, str) and len(item) > TEXT_CHAR_THRESHOLD:
                return True
        return False

    def should_summarize_dict(d: Dict) -> bool:
        if not d:
            return False
        return len(json.dumps(d, ensure_ascii=False)) > JSON_CHAR_THRESHOLD

    def summarize_field(field_name: str, prompt_text: str, value: Any) -> str:
        """Суммаризация одного поля с жестким запретом галлюцинаций"""
        payload = json.dumps(value, ensure_ascii=False, indent=2)

        strict_prompt = (
            f"{prompt_text}\n\n"
            "STRICT RULES - DO NOT VIOLATE:\n"
            "1. NEVER add any information not present in the data\n"
            "2. NEVER make inferences or draw conclusions\n"
            "3. NEVER create new facts or connections\n"
            "4. ONLY summarize what is explicitly in the data\n"
            "5. Keep it factual and concise\n"
            "6. If data is unclear, say so - don't guess\n\n"
            f"DATA TO SUMMARIZE:\n{payload}"
        )

        return llm_call(strict_prompt)

    log("Этап 1: Обработка основной информации о гене...")

    gene_info = all_data.get('gene_info', {})
    if gene_info:
        summaries['gene_basic'] = {
            'symbol': gene_info.get('symbol'),
            'synonyms': gene_info.get('synonyms', []),
            'maploc': gene_info.get('maploc'),
            'nomenclature': gene_info.get('nomenclature', {})
        }

        text_fields_to_summarize = {}
        for field in ['summary', 'description']:
            if gene_info.get(field) and len(gene_info[field]) > TEXT_CHAR_THRESHOLD:
                text_fields_to_summarize[field] = gene_info[field]

        if text_fields_to_summarize:
            try:
                log("  🤖 Суммаризируем текстовые поля gene_info...")
                summaries['gene_description'] = summarize_field(
                    'gene_description',
                    "Summarize the following gene description information FACTUALLY without adding anything:",
                    text_fields_to_summarize
                )
            except Exception as e:
                summaries['gene_description_error'] = str(e)
                summaries['gene_description_raw'] = text_fields_to_summarize

    log("Этап 2: Обработка gene commentaries...")

    commentaries = all_data.get('gene_commentaries', [])
    if commentaries:
        commentary_by_type = {}
        for comment in commentaries:
            comment_type = comment.get('type', 'other')
            if comment_type not in commentary_by_type:
                commentary_by_type[comment_type] = []
            commentary_by_type[comment_type].append(comment)

        for comment_type, type_comments in commentary_by_type.items():
            if should_summarize_list(type_comments):
                try:
                    log(f"  🤖 Суммаризируем {comment_type} commentaries...")

                    type_prompts = {
                        'pathway': "Summarize the pathway information FACTUALLY. List pathways mentioned:",
                        'phenotype': "Summarize the phenotype associations FACTUALLY. List phenotypes mentioned:",
                        'function': "Summarize the functional annotations FACTUALLY. List key functions:",
                        'Generif': "Summarize the gene reference facts FACTUALLY. List key findings:",
                        'expression': "Summarize the expression patterns FACTUALLY. List tissues/cells mentioned:",
                        'interactions': "Summarize the interaction data FACTUALLY. List interacting partners:",
                        'domains': "Summarize the domain information FACTUALLY. List domains mentioned:"
                    }

                    prompt = type_prompts.get(comment_type,
                                              f"Summarize the {comment_type} information FACTUALLY without adding anything:")

                    summaries[f'commentaries_{comment_type}'] = summarize_field(
                        f'commentaries_{comment_type}',
                        prompt,
                        type_comments
                    )
                except Exception as e:
                    summaries[f'commentaries_{comment_type}_error'] = str(e)
                    summaries[f'commentaries_{comment_type}_raw'] = type_comments[:5]
            else:
                summaries[f'commentaries_{comment_type}'] = type_comments

    log("Этап 3: Обработка биологических источников...")

    biosource = all_data.get('biosource', {})
    if biosource:
        organism_info = biosource.get('organism', {})
        if organism_info and should_summarize_dict(organism_info):
            try:
                log("  🤖 Суммаризируем organism info...")
                summaries['organism'] = summarize_field(
                    'organism',
                    "Summarize the organism taxonomic information FACTUALLY:",
                    organism_info
                )
            except Exception as e:
                summaries['organism_error'] = str(e)
                summaries['organism_raw'] = organism_info

    log("Этап 4: Обработка геномных данных...")

    genomics = all_data.get('genomics', {})
    if genomics:
        summaries['genomics_basic'] = {
            'maps_display': genomics.get('maps_display'),
            'na_strand': genomics.get('na_strand')
        }

        location = genomics.get('location', {})
        if location and should_summarize_dict(location):
            try:
                log("  🤖 Суммаризируем genomic location...")
                summaries['genomic_location'] = summarize_field(
                    'genomic_location',
                    "Summarize the genomic location information FACTUALLY:",
                    location
                )
            except Exception as e:
                summaries['genomic_location_error'] = str(e)

    log("Этап 5: Обработка публикаций...")

    publications = all_data.get('publications', [])
    if publications:
        if len(publications) > 10:
            try:
                log("  🤖 Суммаризируем публикации...")
                summaries['publications_summary'] = summarize_field(
                    'publications',
                    "List the PubMed IDs mentioned FACTUALLY:",
                    [p.get('pmid') for p in publications if p.get('pmid')]
                )
            except Exception as e:
                summaries['publications_error'] = str(e)
                summaries['publications_sample'] = publications[:10]
        else:
            summaries['publications'] = publications

    log("Этап 6: Обработка технических данных...")

    technical = all_data.get('technical', {})
    if technical:
        important_tech = {
            'track': technical.get('track', {}),
            'gene_source': technical.get('gene_source', {})
        }
        if should_summarize_dict(important_tech):
            try:
                log("  🤖 Суммаризируем технические данные...")
                summaries['technical_summary'] = summarize_field(
                    'technical',
                    "Summarize the technical metadata FACTUALLY:",
                    important_tech
                )
            except Exception as e:
                summaries['technical_error'] = str(e)
                summaries['technical_raw'] = important_tech

    log("Этап 7: Обработка внешних баз данных...")

    additional = all_data.get('additional', {})
    if additional:
        external_dbs = additional.get('external_dbs', [])
        if external_dbs and len(external_dbs) > 5:
            try:
                log("  🤖 Суммаризируем внешние базы данных...")
                summaries['external_dbs_summary'] = summarize_field(
                    'external_dbs',
                    "List the external database references FACTUALLY:",
                    external_dbs
                )
            except Exception as e:
                summaries['external_dbs_error'] = str(e)
                summaries['external_dbs_sample'] = external_dbs[:10]
        else:
            summaries['external_dbs'] = external_dbs

    log("Этап 8: Финальная суммаризация...")

    try:
        final_prompt_parts = []

        for key, value in summaries.items():
            if key.endswith('_error'):
                continue

            if hasattr(value, 'content'):
                section_text = str(value.content)
            else:
                section_text = json.dumps(value, ensure_ascii=False, indent=2)

            final_prompt_parts.append(f"=== {key.upper()} ===\n{section_text}")

        final_prompt = (
                "Create a WELL-STRUCTURED and READABLE summary of the gene data below.\n\n"
                "🔴 STRICT PROHIBITIONS - DO NOT VIOLATE:\n"
                "1. NEVER add any information not explicitly present in the data\n"
                "2. NEVER make inferences, conclusions, or connections\n"
                "3. NEVER speculate or interpret the data\n"
                "4. NEVER add your own knowledge about the gene\n"
                "5. ONLY use facts directly from the provided data\n"
                "6. If something is unclear from data, don't mention it\n\n"
                "🟢 WHAT TO DO:\n"
                "1. Organize information in clear sections\n"
                "2. Use bullet points for lists\n"
                "3. Keep identifiers and technical terms as they are\n"
                "4. Be concise but comprehensive\n"
                "5. Maintain factual accuracy above all\n\n"
                "GENE DATA:\n" + "\n\n".join(final_prompt_parts)
        )

        log("  🤖 Вызываем финальную суммаризацию...")
        final_response = llm_call(final_prompt)
        summaries['final_protein_article'] = final_response.content if hasattr(final_response, 'content') else str(final_response)

        log("  ✅ Финальная суммаризация завершена!")

    except Exception as e:
        summaries['final_article_error'] = str(e)
        log(f"  ❌ Ошибка финальной суммаризации: {e}")

    log("Этап 10: Формирование результата...")

    result = {
        'section_summaries': summaries,
        'all_sections_count': len(summaries),
        'has_final_article': 'final_article' in summaries,
        'processing_timestamp': datetime.now().isoformat()
    }

    log(f"✅ Суммаризация завершена! Создано {len(summaries)} разделов")

    return result

def process_gene(gene_id: str):
    all_data = extract_ALL_fields_gene(gene_id)
    all_data = summarize_ALL_fields_gene(all_data)
    return all_data

def extract_pmids_from_text(text: str) -> Set[str]:
    """Извлекает все PMID из текста"""
    pmids = set()
    pattern = r'PMID:\s*(\d+)'
    matches = re.findall(pattern, text)
    pmids.update(matches)
    return pmids

def final_process(protein_name):
    print("🚀 ЗАПУСК NCBI-Агента")
    try:
        # 1. Получаем gene_id
        data = {}
        data["gene_name"] = protein_name
        data["found_articles"] = ""

        print(f"🔍 Поиск gene_id для {protein_name}...")
        gene_response = run_super_agent(info=data, steps=1, user_promt_func=set_user_prompt_simple_gene_id, protein=protein_name)
        gene_id = get_gene_id_simple(gene_response)

        if not gene_id:
            print("❌ Не удалось найти gene_id")
            return None

        print(f"✅ Найден gene_id: {gene_id}")

        # 2. Обрабатываем ген
        print("🧬 Обработка данных гена...")
        gene_data = process_gene(gene_id)

        # 3. Получаем суммаризацию
        gene_summary_text = gene_data.get('section_summaries', {}).get('final_protein_article', '')
        if hasattr(gene_summary_text, 'content'):
            gene_summary_text = gene_summary_text.content

        # 4. Извлекаем транскрипты и белки
        print("📋 Извлечение важных транскриптов и белков...")
        t_prompt = f"""
        EXTRACT ONLY IMPORTANT PROTEIN ACCESSIONS from this gene data.

        GENE DATA:
        {gene_summary_text}

        CRITICAL FILTERING RULES - EXTRACT ONLY:
        1. MANE Select proteins
        2. Reviewed/Curated proteins  
        3. Swiss-Prot proteins
        4. Proteins with CCDS association
        5. Main canonical proteins

        IGNORE COMPLETELY:
        - Unreviewed proteins
        - Alternative assembly proteins  
        - Fragment peptides
        - Technical variants
        - Patent submissions
        - Automatic predictions

        RETURN ONLY in this exact format:
        TRANSCRIPTS: [comma-separated list of mRNA accessions]
        PROTEINS: [comma-separated list of protein accessions]

        EXAMPLES:
        For SOX2 data, you should extract:
        TRANSCRIPTS: NM_003106
        PROTEINS: NP_003097.1, P48431

        INSTRUCTIONS:
        1. Extract ONLY important accessions meeting the criteria above
        2. Separate with commas and spaces  
        3. NO other text, NO explanations
        4. If no important proteins found, return: TRANSCRIPTS: PROTEINS:
        """

        transcripts_and_proteins = call_llm_directly(t_prompt)
        if hasattr(transcripts_and_proteins, 'content'):
            transcripts_and_proteins = transcripts_and_proteins.content

        # Безопасное разделение
        if 'TRANSCRIPTS:' in transcripts_and_proteins and 'PROTEINS:' in transcripts_and_proteins:
            transcripts_part = transcripts_and_proteins.split('TRANSCRIPTS: ')[1].split('PROTEINS: ')[0].strip()
            proteins_part = transcripts_and_proteins.split('PROTEINS: ')[1].strip()

            transcripts = [t.strip() for t in transcripts_part.split(',') if t.strip()] if transcripts_part else []
            proteins = [p.strip() for p in proteins_part.split(',') if p.strip()] if proteins_part else []
        else:
            transcripts, proteins = [], []

        print(f"📊 Найдено: {len(transcripts)} транскриптов, {len(proteins)} белков")

        # 5. Обрабатываем каждый белок
        print("🔬 Обработка информации о белках...")
        final_answer = f"=== ОТЧЕТ ПО ГЕНУ {protein_name} (ID: {gene_id}) ===\n\n"
        final_answer += gene_summary_text + "\n\n"

        for i, protein in enumerate(proteins, 1):
            print(f"🔬 Обрабатываем белок {i}/{len(proteins)}: {protein}")
            try:
                protein_result = process_protein(protein)
                if protein_result and 'protein_summaries' in protein_result:
                    protein_summary = protein_result['protein_summaries'].get('final_protein_article', '')
                    if hasattr(protein_summary, 'content'):
                        protein_summary = protein_summary.content
                    final_answer += f"=== БЕЛОК {protein} ===\n{protein_summary}\n\n"
            except Exception as e:
                print(f"⚠️ Ошибка при обработке белка {protein}: {e}")
                final_answer += f"=== БЕЛОК {protein} ===\n❌ Ошибка обработки\n\n"

        print("=" * 50)
        print("✅ Структурная информация собрана")
        print("=" * 50)

        # 6. PubMed поиск с итерациями
        print("🔍 Запуск PubMed поиска...")
        data["gene_info"] = gene_summary_text

        all_pubmed_responses = ""
        all_found_pmids = set()
        max_iterations = 3

        # Первый поиск
        print("📚 Первоначальный поиск в PubMed...")
        pubmed_response = run_super_agent(
            info=data,
            steps=10,
            user_promt_func=set_user_prompt_pubmed_analysis,
            protein=protein_name
        )
        all_pubmed_responses += f"=== ПЕРВОНАЧАЛЬНЫЙ ПОИСК ===\n{pubmed_response}\n\n"

        for i in range(max_iterations):
            print(f"🔄 PubMed итерация {i+1}/{max_iterations}")

            # Извлекаем статьи из предыдущего ответа
            new_articles_text = call_llm_directly(set_extraction_prompt(pubmed_response)).content

            # Обновляем список найденных PMID
            new_pmids = extract_pmids_from_text(new_articles_text)
            new_unique_pmids = new_pmids - all_found_pmids
            all_found_pmids.update(new_pmids)

            print(f"📈 Найдено PMID: {len(new_pmids)} (новых: {len(new_unique_pmids)})")

            # Обновляем found_articles для следующей итерации
            data["found_articles"] = new_articles_text

            # Выполняем агрессивный поиск
            pubmed_response = run_super_agent(
                info=data,
                steps=10,
                user_promt_func=set_aggressive_search_prompt,
                protein=protein_name
            )

            # Сохраняем ответ
            all_pubmed_responses += f"=== ИТЕРАЦИЯ {i+1} ===\n{pubmed_response}\n\n"

            # Пауза между итерациями
            if i < max_iterations - 1:  # Не пауза после последней итерации
                print("⏳ Пауза между итерациями...")
                time.sleep(3)

        # 7. Финальная обработка PubMed результатов
        print("🧹 Очистка и структурирование PubMed результатов...")
        cleaned_pubmed = call_llm_directly(set_cleanup_results_prompt(all_pubmed_responses)).content

        # 8. Формирование финального отчета
        final_answer += f"\n=== ИНФОРМАЦИЯ ПО PUBMED ===\n"
        final_answer += f'\n{cleaned_pubmed}\n'
        final_answer += f"\n📊 СТАТИСТИКА ПОИСКА:\n"
        final_answer += f"• Всего итераций: {max_iterations + 1}\n"
        final_answer += f"• Уникальных статей найдено: {len(all_found_pmids)}\n"
        final_answer += f"• Ген: {data['gene_name']}\n"
        final_answer += f"• Gene ID: {gene_id}\n"
        final_answer += f"• Основные белки: {', '.join(proteins)}\n"

        # 9. Сохраняем результат
        print("💾 Сохранение отчета...")
        with open('gene_protein_report.txt', 'w', encoding='utf-8') as f:
            f.write(final_answer)

        # 10. Сохраняем сырые PubMed данные отдельно
        with open('pubmed_raw_data.txt', 'w', encoding='utf-8') as f:
            f.write(all_pubmed_responses)

        print("=" * 50)
        print("🎉 ОТЧЕТ УСПЕШНО СОЗДАН!")
        print("=" * 50)
        print(f"📁 Основной отчет: gene_protein_report.txt")
        print(f"📁 Сырые данные PubMed: pubmed_raw_data.txt")
        print(f"📊 Найдено статей: {len(all_found_pmids)}")
        print(f"🔬 Обработано белков: {len(proteins)}")
        print("=" * 50)

    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    final_process("NRF2")
