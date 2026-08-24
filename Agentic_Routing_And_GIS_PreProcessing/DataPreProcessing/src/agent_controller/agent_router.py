from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from mock_tools import mock_single_image_vqa, mock_bitemporal_change_analyzer, mock_optical_sar_fusion, mock_region_grounding
import os
from dotenv import load_dotenv
import os

load_dotenv()  # Loads variables from .env

api_key = os.getenv("GROQ_API_KEY_AGENTIC")

print(api_key)

# Paste your Groq API key here!
os.environ["GROQ_API_KEY"] = api_key

def run_query(metadata, user_input):
    # 1. Initialize the Brain
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
    
    # 2. Put our tools in a list
    tools = [
        mock_single_image_vqa, 
        mock_bitemporal_change_analyzer, 
        mock_optical_sar_fusion,
        mock_region_grounding
    ]
    
    # 3. BIND the tools directly to the LLM (This bypasses all AgentExecutors!)
    llm_with_tools = llm.bind_tools(tools)
    
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
    
    # Create the exact prompt structure the LLM expects
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Image Metadata: {metadata}\nUser Query: {user_input}")
    ]
    
    print(f"\n📨 RECEIVED QUERY: '{user_input}'")
    print(f"📄 METADATA: {metadata}")
    print("-" * 50)
    
    # 4. Invoke the LLM directly
    response = llm_with_tools.invoke(messages)
    
    print("\n🔍 --- SIH AUDITABLE EXECUTION TRACE ---")
    
    # 5. Extract the routing decision
    if response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            print(f"➡️ Tool Selected: {tool_name}")
            print(f"⚙️ Parameters Configured: {tool_args}")
            
            # Dynamically execute the mock python function
            tool_mapping = {tool.name: tool for tool in tools}
            selected_tool = tool_mapping[tool_name]
            tool_output = selected_tool.invoke(tool_args)
            
            print(f"✅ Tool Output: {tool_output}")
            print("-" * 50)
            print(f"🤖 FINAL ANSWER:\n{tool_output}\n")
    else:
        print("❌ No tool was selected.")
        print("-" * 50)
        print(f"🤖 FINAL ANSWER:\n{response.content}\n")

if __name__ == "__main__":
    
    fake_metadata = "User uploaded 1 image. Modality: OPTICAL_OR_MULTISPECTRAL."
    user_query = "Highlight the water body referred to in the query."
    
    run_query(fake_metadata, user_query)