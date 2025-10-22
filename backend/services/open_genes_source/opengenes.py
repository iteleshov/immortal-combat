# https://github.com/longevity-genie/opengenes-mcp
# Download and install uv
# curl -LsSf https://astral.sh/uv/install.sh | sh
# pip install requests beautifulsoup4 lxml

from smolagents import ToolCollection, ToolCallingAgent, OpenAIServerModel, Tool
from mcp import StdioServerParameters
import os
import json
import requests, re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

class ReadScholarlyByDOI(Tool):
    name = "read_scholarly_by_doi"
    description = (
        "Читает статью по DOI. Приоритет: PubMed→PMC (open access). "
        "Если PMC нет — возвращает абстракт с PubMed."
    )

    # 1) inputs — ключи должны совпадать с сигнатурой forward()
    inputs = {
        "doi": {"type": "string", "required": True, "description": "Напр.: 10.1111/j.1474-9726.2009.00493.x"}
    }

    # 2) output_type — СТРОКА; подробная схема — в output_schema (опционально)
    output_type = "object"
    output_schema = {
        "type": "object",
        "properties": {
            "source": {"type": "string"},
            "url":    {"type": "string"},
            "title":  {"type": "string"},
            "text":   {"type": "string"}
        },
        "required": ["source", "url"]
    }

    # 3) ВАЖНО: метод называется forward и принимает РОВНО те аргументы, что в inputs
    def forward(self, doi: str) -> dict:
        headers = {"User-Agent": "Mozilla/5.0"}
        # 1) Поиск на PubMed
        pm_url = f"https://pubmed.ncbi.nlm.nih.gov/?term={doi}"
        r = requests.get(pm_url, timeout=20, headers=headers)
        r.raise_for_status()
        s = BeautifulSoup(r.text, "lxml")
        hit = s.select_one("article.full-docsum a.docsum-title")
        if not hit:
            return {"source": "pubmed", "url": pm_url, "title": None, "text": "No PubMed hit found for DOI."}

        art_url = "https://pubmed.ncbi.nlm.nih.gov" + hit.get("href")
        r2 = requests.get(art_url, timeout=20, headers=headers)
        r2.raise_for_status()
        s2 = BeautifulSoup(r2.text, "lxml")
        title_el = s2.select_one("h1.heading-title")
        title = title_el.get_text(" ", strip=True) if title_el else None

        # 2) Ищем PMCID
        pmcid = None
        for span in s2.select("span.identifier"):
            m = re.search(r"PMCID:\s*(PMC\d+)", span.get_text(" ", strip=True))
            if m:
                pmcid = m.group(1)
                break

        if pmcid:
            pmc_url = f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/"
            rp = requests.get(pmc_url, timeout=20, headers=headers)
            rp.raise_for_status()
            sp = BeautifulSoup(rp.text, "lxml")
            body = sp.select_one("div#maincontent")
            text = (body.get_text("\n", strip=True) if body else sp.get_text("\n", strip=True))[:300000]
            return {"source": "pmc", "url": pmc_url, "title": title, "text": text}

        # 3) Фолбэк — абстракт на PubMed
        abst = s2.select_one("div.abstract, div#enc-abstract")
        text = (abst.get_text("\n", strip=True) if abst else s2.get_text("\n", strip=True))[:300000]
        return {"source": "pubmed", "url": art_url, "title": title, "text": text}


# configuration
def set_server(server_name="opengenes-mcp-server"):
    server = StdioServerParameters(
        command="uvx",
        args=[server_name, "stdio"]
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


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SYSTEM_PROMPT_PATH = os.path.join(BASE_DIR, 'opengenes_system_prompt.txt')
def set_user_prompt_og(gene):
    return f"""
            What are:
            - Longevity/lifespan/healthspan association
            - Modification effects
            - Known genetic interventions
            - Disease involvement
            - Table of Allelic polymorphisms: [...] (columns: Polymorphism, Polymorphism type, Association type, Significance, Research type, Link to details)
            for the gene: {gene} across different species?
            Make sure to include the whole list of SNPs, do not truncate it.
            If some information is not available in the base for this name of the gene try to find synonyms and find and fetch data for them.
            If this attempt also fails return "Info not available".

            STRICTLY:
            Do NOT include raw double quotes (") or backslashes (\) inside argument values. If a value contains them, **remove** these characters.
            1) When constructing SQL-like conditions, use **single quotes** around values INSIDE the condition string. Example:  OK →  "Symbol = 'TERT'".  
               The **value itself** must be a clean atom (e.g., TERT), never "'TERT'" or "\"TERT\"" or "TERT\"".
            2) If you need LIKE, write the percent signs in the condition, not inside the value.  
            3) Always call the tool 'final_answer' at the end
        """

def set_user_prompt_fetch(link, gene):
    return f"""
            Task: For each provided URL, return the article abstract text if present.

            Policy:
            1) Try read_url/open_url first. If you get cleaned text/markdown or raw HTML, extract Abstract:
               - Prefer JSON-LD (`ScholarlyArticle.abstract`/`description`).
               - Else headings: Abstract|Summary (take the following paragraph block until next heading).
               - Else meta tags: citation_abstract, dc.description, og:description, twitter:description.
               - If you see DOI — call read_scholarly_by_doi at first.
            2) If empty/not present or page asks for JS: use browser-use tools:
               - browser_navigate(url)
               - if needed, browser_click on “Abstract”, “Show more”, “Article info”
               - browser_extract_content() or query a specific selector:
                   * Nature: section[id^="Abs"] .c-article-section__content
                   * ScienceDirect: #abstracts .abstract.author, meta[name="citation_abstract"]
               - Extract Abstract again via the same rules.
            Output a JSON with the following schema:
            {{
              "items": [{{
                "url": str,
                "found": bool,
                "abstract": str,
                "method": "read_url"|"browser",
                "evidence": [{{"selector_or_tag": str, "snippet": str}}]
                "Modification Effects": "<What are the effects of this exact modification>",
                "Longevity Association": "<if applicalble>"
              }}]
            }}
            All the info fetched from the links must be realated to {gene}
            URL: {link}
        """

def sanitize(s: str) -> str:
    return s.strip().replace('"', '').replace("'", "").replace("\\", "").replace("%", "")


def run_query(
    gene,
    model=set_model(),
    trust_remote_code=True,
    structured_output=False
):
    system_prompt = SYSTEM_PROMPT
    user_prompt_og = set_user_prompt_og(gene)
    server_opengenes = StdioServerParameters(
        command="uvx",
        args=["opengenes-mcp", "stdio"]
    )
    server_web_tools = StdioServerParameters(
        command="npx",
        args=["-y", "@just-every/mcp-read-website-fast"]
    )

    with ToolCollection.from_mcp(
        server_parameters=server_opengenes,
        trust_remote_code=trust_remote_code,
        structured_output=structured_output
    ) as tools:
        agent = ToolCallingAgent(
            model=model,
            tools=[*tools.tools],
            add_base_tools=False,
            max_steps=5,
        )
        agent.prompt_templates["system_prompt"] = system_prompt
        opengenes_text = agent.run(user_prompt_og)

    agent_extractor = ToolCallingAgent(
        model=model,
        tools=[],
        add_base_tools=False,
        max_steps=1,
    )
    links = agent_extractor.run(
        f'''
        Extract all hyperlinks from the document and return only a JSON:
        {{
            "links":
            [
                {{
                    "Polymorphism": "<Polymorphism ID>",
                    "link": "<link>"
                }}    
            ]
        }}
        Document: {sanitize(opengenes_text)}
        '''
    )
    web_array = []
    if links:
        with ToolCollection.from_mcp(
                server_parameters=server_web_tools,
                trust_remote_code=True,
                structured_output=True
            ) as tools:
            agent = ToolCallingAgent(
                model=model,
                tools=[*tools.tools],
                add_base_tools=False,
                max_steps=1,
            )
            print('Fetching from URLs')
            # with ThreadPoolExecutor(max_workers=min(8, len(links))) as ex:
            #         futures = [
            #             ex.submit(agent.run, set_user_prompt_fetch(link, gene))
            #             for link in json.loads(links)['links']
            #         ]
            #         web_array = [f.result() for f in futures]
            for item in json.loads(links)['links']:
                link = item['link']
                web_array.append(agent.run(set_user_prompt_fetch(link, gene)))

    return opengenes_text, web_array

