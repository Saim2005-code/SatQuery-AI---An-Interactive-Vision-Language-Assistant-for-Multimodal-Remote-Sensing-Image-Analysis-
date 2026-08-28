# BackEnd/agent_router.py
import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from mock_tools import mock_single_image_vqa, mock_bitemporal_change_analyzer, mock_optical_sar_fusion, mock_region_grounding

load_dotenv()
# Ensure your .env file has GROQ_API_KEY_AGENTIC set!
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY_AGENTIC", "")

def execute_satquery_agent(metadata_str, user_query):
    start_time = time.time()
    
    # 1. Initialize the LLM (Using a standard Groq model)
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
    
    # 2. Bind Tools
    tools = [
        mock_single_image_vqa, 
        mock_bitemporal_change_analyzer, 
        mock_optical_sar_fusion,
        mock_region_grounding
    ]
    llm_with_tools = llm.bind_tools(tools)
    
    # 3. System Prompt Execution
    system_prompt = """
    You are SatQuery AI, an autonomous remote sensing orchestration agent.
    Your job is to route user queries to the correct specialized tool.
    
    ROUTING RULES:
    1. If the user asks a general question about a SINGLE image, use 'single_image_vqa'.
    2. If the user asks to FIND, HIGHLIGHT, or LOCATE a specific object in an image, use 'region_grounding'.
    3. If the user asks about CHANGES or compares TWO images from different dates, use 'bitemporal_change_analyzer'.
    4. If the user mentions CLOUDS or asks to use SAR and Optical data together, use 'optical_sar_fusion'.
    
    You must execute exactly ONE tool. Do not try to answer the question yourself.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Image Metadata: {metadata_str}\nUser Query: {user_query}")
    ]
    
    print(f"🧠 Agent Routing Query: {user_query}")
    response = llm_with_tools.invoke(messages)
    
    # 4. Prepare the default trace for React
    latency = int((time.time() - start_time) * 1000)
    trace = {
        "classified_task": "GENERAL_QA",
        "invoked_tool": "none",
        "confidence_score": "85.2%",
        "latency_ms": latency
    }
    answer = response.content
    bounding_box = None

    # 5. Extract Tool Execution for the UI
    # Inside agent_router.py, update the tool execution section:
    if response.tool_calls:
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
    
        # Inject actual saved file paths into the tool arguments dynamically!
        # (Assuming saved_files is accessible or passed in metadata)
        tool_args["image_path"] = metadata_str # or pass the actual file path list
    
        tool_mapping = {tool.name: tool for tool in tools}
        selected_tool = tool_mapping[tool_name]
        tool_output = selected_tool.invoke(tool_args)
    
        answer = tool_output

    return answer, trace, bounding_box