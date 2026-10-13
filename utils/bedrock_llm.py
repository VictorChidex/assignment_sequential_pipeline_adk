# =============================================================================
# FILE: utils/bedrock_llm.py
# PURPOSE:
#   Wraps ChatBedrockConverse (LangChain) as an ADK BaseLlm so we can use
#   AWS Bedrock with our bearer token, exactly like the other notebooks.
#   Registers itself as the handler for any "bedrock/..." model string.
# =============================================================================

import asyncio
import json
import logging
import os
from typing import AsyncGenerator

from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.models.registry import LLMRegistry
from google.genai import types
from langchain_aws import ChatBedrockConverse
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from typing_extensions import override

logger = logging.getLogger(__name__)


class BedrockLlm(BaseLlm):
    """ADK model wrapper for AWS Bedrock using ChatBedrockConverse."""

    @classmethod
    def supported_models(cls) -> list[str]:
        return [r"bedrock/.*"]

    def _build_client(self):
        model_id = self.model.replace("bedrock/", "", 1)
        return ChatBedrockConverse(
            model=model_id,
            region_name=os.getenv("AWS_REGION_NAME", "ap-southeast-2"),
        )

    def _to_lc_messages(self, llm_request: LlmRequest) -> list:
        messages = []

        if llm_request.config and llm_request.config.system_instruction:
            si = llm_request.config.system_instruction
            text = (
                " ".join(p.text for p in si.parts if p.text)
                if hasattr(si, "parts")
                else str(si)
            )
            if text:
                messages.append(SystemMessage(content=text))

        for content in llm_request.contents:
            role = content.role
            parts = content.parts or []

            if role == "user":
                tool_results = [p for p in parts if p.function_response]
                if tool_results:
                    for p in tool_results:
                        resp = p.function_response.response
                        messages.append(
                            ToolMessage(
                                content=json.dumps(resp) if isinstance(resp, dict) else str(resp),
                                tool_call_id=p.function_response.id or p.function_response.name,
                            )
                        )
                else:
                    text = " ".join(p.text for p in parts if p.text)
                    messages.append(HumanMessage(content=text))

            elif role == "model":
                text = " ".join(p.text for p in parts if p.text)
                lc_tool_calls = [
                    {
                        "id": p.function_call.id or p.function_call.name,
                        "name": p.function_call.name,
                        "args": p.function_call.args or {},
                        "type": "tool_call",
                    }
                    for p in parts
                    if p.function_call
                ]
                messages.append(AIMessage(content=text, tool_calls=lc_tool_calls))

        return messages

    @staticmethod
    def _fix_schema(schema) -> dict:
        if schema is None:
            return {"type": "object", "properties": {}}

        if hasattr(schema, "model_dump"):
            raw = schema.model_dump(exclude_none=True)
        elif isinstance(schema, dict):
            raw = schema
        else:
            try:
                raw = json.loads(schema.model_dump_json(exclude_none=True))
            except Exception:
                return {"type": "object", "properties": {}}

        def _fix(node):
            if not isinstance(node, dict):
                return node
            out = {}
            for k, v in node.items():
                if k == "type" and isinstance(v, str):
                    out[k] = v.lower()
                elif isinstance(v, dict):
                    out[k] = _fix(v)
                elif isinstance(v, list):
                    out[k] = [_fix(i) for i in v]
                else:
                    out[k] = v
            return out

        return _fix(raw)

    def _to_lc_tools(self, llm_request: LlmRequest) -> list:
        if not llm_request.config or not llm_request.config.tools:
            return []

        lc_tools = []
        for adk_tool in llm_request.config.tools:
            for fn in getattr(adk_tool, "function_declarations", None) or []:
                params = self._fix_schema(fn.parameters)
                if params.get("type") != "object":
                    params = {"type": "object", "properties": {}}

                lc_tools.append({
                    "type": "function",
                    "function": {
                        "name": fn.name,
                        "description": fn.description or "",
                        "parameters": params,
                    },
                })
        return lc_tools

    @override
    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:

        client = self._build_client()
        messages = self._to_lc_messages(llm_request)
        lc_tools = self._to_lc_tools(llm_request)

        if lc_tools:
            client = client.bind_tools(lc_tools)

        response: AIMessage = await asyncio.get_event_loop().run_in_executor(
            None, client.invoke, messages
        )

        parts = []
        if response.content:
            parts.append(types.Part(text=str(response.content)))

        for tc in response.tool_calls or []:
            parts.append(
                types.Part(
                    function_call=types.FunctionCall(
                        id=tc.get("id", tc["name"]),
                        name=tc["name"],
                        args=tc.get("args", {}),
                    )
                )
            )

        yield LlmResponse(
            content=types.Content(role="model", parts=parts),
            partial=False,
        )


LLMRegistry.register(BedrockLlm)
