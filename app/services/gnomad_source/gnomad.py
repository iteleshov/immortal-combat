from smolagents import ToolCollection, InferenceClientModel, OpenAIServerModel, ToolCallingAgent
from mcp import StdioServerParameters
import os


absolute_path_to_mcp = ""

MODEL = "Qwen/Qwen3-235B-A22B-Thinking-2507"

os.environ['NEBIUS_API_KEY'] = open('secret.txt', 'r').read().strip()

def set_server(absolute_path_to_mcp):
    server = StdioServerParameters(
        command="node",
        args=[absolute_path_to_mcp + "dist/index.js"]
    )
    return server

def set_model(
    model_name=MODEL,
    api_key=os.environ["NEBIUS_API_KEY"],
    api_base="https://api.studio.nebius.com/v1/",
    temperature=0,
):
    model = OpenAIServerModel(
        model_id=model_name,
        api_key=api_key,
        api_base=api_base,
        temperature=temperature,
    )
    return model

SYSTEM_PROMPT = """
You are an expert bioinformatician assistant. 
Analyze gnomAD v4.1.0 data for the specified gene using available tools. 
Prioritize retrieving and summarizing information on variants classified 
as 'Pathogenic', 'Likely pathogenic', or 'Pathogenic/Likely pathogenic' in ClinVar. 
Since direct API filtering is not possible, combine results from gene variant listing and 
individual variant ClinVar lookup tools. Focus the summary on the clinical significance and 
potential functional impact of the identified variants. 
Include source URLs.
"""

def set_user_prompt(GENE_QUERY):
    return f"""
Analyze gene '{GENE_QUERY}' in gnomAD v4.1.0. 
Find variants with ClinVar significance 'Pathogenic', 'Likely pathogenic', or 'Pathogenic/Likely pathogenic'.
Summarize their clinical significance and potential functional impact based on gnomAD data. 
Provide source URLs. 
If none found, state: 'No qualifying variants found in gnomAD v4.1.0 for gene {GENE_QUERY}.'
    """

def run_query(
        gene,
        server=set_server(absolute_path_to_mcp),
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
            max_steps=7 ,
        )
        agent.prompt_templates["system_prompt"] = system_prompt
        result = agent.run(user_prompt)

    return result

