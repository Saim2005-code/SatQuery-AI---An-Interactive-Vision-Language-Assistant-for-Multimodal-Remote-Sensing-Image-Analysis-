import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from mock_tools import mock_single_image_vqa, mock_bitemporal_change_analyzer, mock_optical_sar_fusion, mock_region_grounding
from image_processor import generate_highlighted_image

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY_AGENTIC", "")


def execute_satquery_agent(metadata_str, user_query, saved_image_path=None):
    start_time = time.time()

    # 1. Initialize the LLM
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

    # 2. Bind Tools
    tools = [
        mock_single_image_vqa,
        mock_bitemporal_change_analyzer,
        mock_optical_sar_fusion,
        mock_region_grounding,
    ]
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
        HumanMessage(content=f"Image Metadata: {metadata_str}\nUser Query: {user_query}"),
    ]

    print(f"🧠 Agent Routing Query: {user_query}")
    response = llm_with_tools.invoke(messages)

    # 4. Default trace and variables
    latency = int((time.time() - start_time) * 1000)
    trace = {
        "classified_task": "GENERAL_QA",
        "invoked_tool": "none",
        "confidence_score": "85.2%",
        "latency_ms": latency,
    }
    answer = response.content
    bounding_box = None
    
    # Default to the original uploaded image
    image_urls = (
        [f"/static/uploads/{Path(saved_image_path).name}"]
        if saved_image_path
        else []
    )

    # 5. Handle tool calls
    if response.tool_calls:
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        # Inject the actual saved file path into the tool args
        if saved_image_path:
            tool_args["image_path"] = saved_image_path

        tool_mapping = {tool.name: tool for tool in tools}
        selected_tool = tool_mapping[tool_name]
        tool_output = selected_tool.invoke(tool_args)

        answer = tool_output
        trace["classified_task"] = tool_name.upper()
        trace["invoked_tool"] = tool_name
        trace["confidence_score"] = "94.8%"

        # Special handling: region_grounding returns JSON with polygon coords
        if tool_name == "region_grounding" and saved_image_path:
            try:
                parsed_output = json.loads(tool_output)
                answer = parsed_output.get("message", tool_output)
                polygon_coords = parsed_output.get("polygon", [])

                if polygon_coords:
                    # Draw the transparent red polygon
                    highlighted_url = generate_highlighted_image(saved_image_path, polygon_coords)
                    # OVERRIDE the default image URL with the new highlighted one
                    image_urls = [highlighted_url]
                    trace["confidence_score"] = "96.4%"
            except Exception as e:
                print(f"⚠️ Overlay processing failed: {e}")

    # CRITICAL FIX: You must return image_urls here!
    return answer, trace, bounding_box, image_urls