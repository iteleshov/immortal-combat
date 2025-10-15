# https://github.com/longevity-genie/opengenes-mcp
# Download and install uv
# curl -LsSf https://astral.sh/uv/install.sh | sh


from smolagents import ToolCollection, ToolCallingAgent, OpenAIServerModel
from mcp import StdioServerParameters
import os


# configuration
os.environ['NEBIUS_API_KEY'] = open('secret.txt', 'r').read().strip()
def set_server():
    server = StdioServerParameters(
        command="uvx",
        args=["opengenes-mcp", "stdio"]
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


SYSTEM_PROMPT = open('opengenes_system_prompt.txt', 'r').read()
def set_user_prompt(gene):
    return f"""
            What are:
            - Longevity/lifespan/healthspan association
            - Modification effects
            - Known genetic interventions
            - Disease involvement
            for the gene: {gene} across different species?
            If there are any known synonyms for the Gene use them to .
            If some information is not available in the base for this name of the gene try to find synonyms and find and fetch data for them.
            If this attampt alse fails return "Info not available".
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
            max_steps=5,
        )
        agent.prompt_templates["system_prompt"] = system_prompt
        result = agent.run(user_prompt)
    
    return result

