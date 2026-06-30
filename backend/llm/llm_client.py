import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    def __init__(self) -> None:
        self.provider = os.getenv("LLM_PROVIDER", "mock").lower().strip()
        self.timeout = httpx.Timeout(120.0, connect=20.0)

    async def generate_json(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        if self.provider == "openai":
            return await self._openai_chat(system_prompt, user_prompt, temperature)
        if self.provider == "qwen":
            return await self._qwen_chat(system_prompt, user_prompt, temperature)
        return self._mock_response()

    async def _openai_chat(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is missing. Set LLM_PROVIDER=mock for offline demo.")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        return await self._post_chat(
            f"{base_url}/chat/completions",
            api_key,
            model,
            system_prompt,
            user_prompt,
            temperature,
        )

    async def _qwen_chat(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise RuntimeError("DASHSCOPE_API_KEY is missing. Set LLM_PROVIDER=mock for offline demo.")
        model = os.getenv("QWEN_MODEL", "qwen-plus")
        return await self._post_chat(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            api_key,
            model,
            system_prompt,
            user_prompt,
            temperature,
        )

    async def _post_chat(
        self,
        url: str,
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
    ) -> str:
        payload: dict[str, Any] = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
        except httpx.TimeoutException as exc:
            raise RuntimeError("模型接口超时，请换 qwen-plus/gpt-4o-mini 或稍后重试。") from exc
        except httpx.HTTPError as exc:
            raise RuntimeError(f"模型接口网络错误：{exc}") from exc

        if response.status_code >= 400:
            raise RuntimeError(f"模型接口返回错误 {response.status_code}: {response.text[:500]}")
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _mock_response(self) -> str:
        return """
{
  "dance_analysis": "这支舞适合做成镜头感强、轮廓清楚的女团舞台造型。动作中如果包含跳跃、转身和手部线条，服装需要兼顾显瘦、舒展和不走光。",
  "style_keywords": ["女团舞台", "甜酷", "短款上衣", "高腰下装", "亮面配饰"],
  "reference_sources": [
    "NewJeans《Super Shy》清爽运动女团风",
    "IVE《I AM》利落短外套与高腰线比例",
    "BLACKPINK《As If It's Your Last》甜酷撞色舞台"
  ],
  "outfits": [
    {
      "name": "平价甜酷练习室舞台套装",
      "concept": "用短款白色上衣和黑色百褶裙做清晰腰线，适合校园汇演和团舞。",
      "image_query": "kpop sweet cool dance outfit white crop top pleated skirt",
      "total_price": 236,
      "reference": "参考 NewJeans 清爽练习室风",
      "items": [
        {"type": "上衣", "name": "白色短款修身T恤", "price": 59, "keyword": "白色 短款 修身 T恤 女 舞蹈"},
        {"type": "下装", "name": "黑色高腰百褶短裙", "price": 69, "keyword": "黑色 高腰 百褶裙 舞台"},
        {"type": "鞋子", "name": "白色厚底运动鞋", "price": 89, "keyword": "白色 厚底 运动鞋 女"},
        {"type": "配饰", "name": "银色星星发夹", "price": 19, "keyword": "银色 星星 发夹 舞台"}
      ]
    },
    {
      "name": "甜美元气彩色套装",
      "concept": "彩色短开衫搭配牛仔短裙，画面明亮，适合活泼甜美风歌曲。",
      "image_query": "cute idol stage outfit pastel cardigan denim skirt",
      "total_price": 312,
      "reference": "参考 STAYC / IVE 甜美打歌服",
      "items": [
        {"type": "上衣", "name": "粉色短款针织开衫", "price": 88, "keyword": "粉色 短款 针织开衫 女"},
        {"type": "下装", "name": "浅蓝高腰牛仔短裙", "price": 86, "keyword": "浅蓝 高腰 牛仔短裙"},
        {"type": "鞋子", "name": "白粉拼色老爹鞋", "price": 108, "keyword": "白粉 拼色 老爹鞋 女"},
        {"type": "配饰", "name": "蝴蝶结发带与耳夹", "price": 30, "keyword": "蝴蝶结 发带 耳夹 舞台"}
      ]
    },
    {
      "name": "帅气黑银短外套套装",
      "concept": "黑色短夹克加工装裙裤，适合力度强、卡点多的舞蹈。",
      "image_query": "kpop black silver stage outfit cropped jacket cargo skirt",
      "total_price": 428,
      "reference": "参考 aespa《Drama》黑银未来感舞台",
      "items": [
        {"type": "上衣", "name": "黑色短款机车夹克", "price": 158, "keyword": "黑色 短款 机车夹克 女"},
        {"type": "下装", "name": "灰黑工装半裙裤", "price": 98, "keyword": "灰黑 工装 半裙裤 女"},
        {"type": "鞋子", "name": "黑色厚底马丁靴", "price": 139, "keyword": "黑色 厚底 马丁靴 女"},
        {"type": "配饰", "name": "银色链条腰链", "price": 33, "keyword": "银色 链条 腰链 舞台"}
      ]
    },
    {
      "name": "灵动薄纱层次套装",
      "concept": "轻薄外搭和A字裙增强旋转时的飘动感，适合 lyrical jazz 或灵动女团舞。",
      "image_query": "flowy dance stage outfit sheer cardigan a line skirt",
      "total_price": 536,
      "reference": "参考 LE SSERAFIM 柔韧线条舞台",
      "items": [
        {"type": "上衣", "name": "米白吊带加薄纱罩衫", "price": 168, "keyword": "米白 吊带 薄纱 罩衫 女"},
        {"type": "下装", "name": "渐变纱质A字短裙", "price": 149, "keyword": "渐变 纱裙 A字 短裙"},
        {"type": "鞋子", "name": "裸色软底舞蹈鞋", "price": 119, "keyword": "裸色 软底 舞蹈鞋 女"},
        {"type": "配饰", "name": "珍珠发链与细项链", "price": 100, "keyword": "珍珠 发链 细项链 舞台"}
      ]
    },
    {
      "name": "高级亮片主舞台套装",
      "concept": "亮片短上衣和皮质短裤在灯光下更抓镜头，适合正式比赛或晚会中心位。",
      "image_query": "glitter kpop stage outfit sequin crop top leather shorts boots",
      "total_price": 758,
      "reference": "参考 BLACKPINK 高光舞台造型",
      "items": [
        {"type": "上衣", "name": "银色亮片短款上衣", "price": 238, "keyword": "银色 亮片 短款 上衣 舞台"},
        {"type": "下装", "name": "黑色高腰皮质短裤", "price": 169, "keyword": "黑色 高腰 皮短裤 女"},
        {"type": "鞋子", "name": "黑色及膝舞台靴", "price": 269, "keyword": "黑色 及膝 靴 舞台"},
        {"type": "配饰", "name": "水钻耳饰和手套", "price": 82, "keyword": "水钻 耳饰 手套 舞台"}
      ]
    }
  ],
  "styling_notes": ["短款上衣配高腰下装可以拉高比例。", "正式舞台建议提前试跳，确认转身和抬手不会走光。", "同队成员可统一主色，再用配饰区分站位。"]
}
"""
