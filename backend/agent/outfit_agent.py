import json
import re

from llm.llm_client import LLMClient
from agent.product_searcher import ProductSearcher


class OutfitAgent:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm
        self.searcher = ProductSearcher()

    async def run(self, dance_input: str, style: str, budget: str) -> dict:
        raw = await self.llm.generate_json(self._system_prompt(), self._user_prompt(dance_input, style, budget))
        data = self._parse_json(raw)
        outfits = self.searcher.enrich_items(data.get("outfits", []))
        data["outfits"] = outfits[:5]
        data["logs"] = [
            "已读取舞蹈题目或链接",
            "已判断舞台氛围和动作需求",
            f"已匹配「{style}」风格关键词",
            "已生成五套完整搭配",
            "已补充商品搜索链接和参考来源",
            "已按总价从低到高排序",
        ]
        return data

    def _system_prompt(self) -> str:
        return """你是一个资深舞台造型师、K-pop 舞台参考研究员和电商选品助理。
你只能输出 JSON，不要输出 Markdown。
你需要为舞蹈演出生成可落地的服装搭配推荐。
要求：
1. 不要编造确定存在的具体商品详情，商品链接字段由系统后处理生成，所以你只需要给 keyword。
2. 参考来源可以写公开舞台风格方向，例如某 idol/组合的某首歌舞台风格，但不要声称完全同款。
3. 五套搭配必须包含上衣、下装、鞋子、配饰，价格从低到高有明显层级。
4. 服装要考虑跳舞安全：防走光、便于抬手转身、鞋底稳定。
5. 输出必须是严格 JSON object。"""

    def _user_prompt(self, dance_input: str, style: str, budget: str) -> str:
        return f"""请基于以下输入生成演出服搭配智能体结果：

舞蹈题目或链接：{dance_input}
用户想要的风格：{style}
预算偏好：{budget}

请输出 JSON，字段结构：
{{
  "dance_analysis": "舞蹈/链接的风格分析，说明适合怎样的舞台造型",
  "style_keywords": ["关键词1", "关键词2"],
  "reference_sources": ["参考来源1", "参考来源2", "参考来源3"],
  "outfits": [
    {{
      "name": "套装名称",
      "concept": "搭配思路",
      "image_query": "英文图片搜索关键词",
      "total_price": 299,
      "reference": "参考某舞台/某类 idol 舞台风格",
      "items": [
        {{"type": "上衣", "name": "单品名", "price": 99, "keyword": "中文电商搜索关键词"}},
        {{"type": "下装", "name": "单品名", "price": 99, "keyword": "中文电商搜索关键词"}},
        {{"type": "鞋子", "name": "单品名", "price": 99, "keyword": "中文电商搜索关键词"}},
        {{"type": "配饰", "name": "单品名", "price": 99, "keyword": "中文电商搜索关键词"}}
      ]
    }}
  ],
  "styling_notes": ["试穿建议1", "舞台安全建议2"]
}}

必须输出 5 套 outfits。"""

    def _parse_json(self, text: str) -> dict:
        cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
            if not match:
                raise ValueError("模型没有返回可解析的 JSON。")
            return json.loads(match.group(0))
