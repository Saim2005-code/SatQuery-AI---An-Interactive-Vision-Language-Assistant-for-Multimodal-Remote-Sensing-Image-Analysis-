import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from mtools import (
    mock_single_image_vqa,
    mock_bitemporal_change_analyzer,
    mock_optical_sar_fusion,
    mock_region_grounding
)

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY_AGENTIC") or os.getenv("GROQ_API_KEY")
if api_key:
    os.environ["GROQ_API_KEY"] = api_key

# FIX: tools have different image-arg schemas. single_image_vqa / region_grounding
# want a single "image_path"; bitemporal_change_analyzer wants a
# "image_path_before" / "image_path_after" pair. Blindly injecting "image_path"
# into every tool_args dict (the old behavior) broke bitemporal the moment it
# was given a real image, since its Pydantic schema has no such field.
TOOLS_ACCEPTING_SINGLE_IMAGE = {"single_image_vqa", "region_grounding"}
TOOLS_ACCEPTING_IMAGE_PAIR = {"bitemporal_change_analyzer"}


def execute_agent_route(
    metadata: str,
    user_input: str,
    image_path: str = None,
    image_path_before: str = None,
    image_path_after: str = None,
) -> dict:
    """
    Executes the agent router and returns a structured dictionary
    containing the audit trace, parameters, and outputs.

    image_path: used for single-image tools (VQA, region grounding).
    image_path_before / image_path_after: used for the bi-temporal tool.
    """
    start_time = time.time()

    # 1. Initialize Tools
    tools = [
        mock_single_image_vqa,
        mock_bitemporal_change_analyzer,
        mock_optical_sar_fusion,
        mock_region_grounding
    ]

    # 2. Bind Tools directly to LLM
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    # 3. System Prompt
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
        HumanMessage(content=f"Image Metadata: {metadata}\nUser Query: {user_input}")
    ]

    # 4. Invoke LLM
    response = llm_with_tools.invoke(messages)
    latency = time.time() - start_time

    # 5. Parse Decision & Execute Specialist Tool
    if response.tool_calls:
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        # FIX: only inject the image argument(s) that this specific tool's
        # schema actually declares, instead of always injecting "image_path".
        if tool_name in TOOLS_ACCEPTING_SINGLE_IMAGE and image_path:
            tool_args["image_path"] = image_path
        elif tool_name in TOOLS_ACCEPTING_IMAGE_PAIR:
            if image_path_before:
                tool_args["image_path_before"] = image_path_before
            if image_path_after:
                tool_args["image_path_after"] = image_path_after

        tool_mapping = {t.name: t for t in tools}
        selected_tool = tool_mapping[tool_name]
        tool_output = selected_tool.invoke(tool_args)

        return {
            "status": "SUCCESS",
            "tool_name": tool_name,
            "tool_args": tool_args,
            "tool_output": str(tool_output),
            "latency": latency,
            "final_answer": str(tool_output)
        }
    else:
        return {
            "status": "NO_TOOL_SELECTED",
            "tool_name": None,
            "tool_args": {},
            "tool_output": None,
            "latency": latency,
            "final_answer": response.content
        }


def run_query(metadata: str, user_input: str, image_path: str = None,
              image_path_before: str = None, image_path_after: str = None):
    """CLI helper to execute and print formatted audit traces to stdout."""
    print(f"\n📨 RECEIVED QUERY: '{user_input}'")
    print(f"📄 METADATA: {metadata}")
    print("-" * 50)

    result = execute_agent_route(metadata, user_input, image_path, image_path_before, image_path_after)

    print("\n🔍 --- SIH AUDITABLE EXECUTION TRACE ---")
    if result["tool_name"]:
        print(f"➡️ Tool Selected: {result['tool_name']}")
        print(f"⚙️ Parameters Configured: {result['tool_args']}")
        print(f"✅ Tool Output: {result['tool_output']}")
    else:
        print("❌ No tool was selected.")

    print("-" * 50)
    print(f"🤖 FINAL ANSWER:\n{result['final_answer']}\n")
    return result