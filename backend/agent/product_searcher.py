from urllib.parse import quote_plus


class ProductSearcher:
    def enrich_items(self, outfits: list[dict]) -> list[dict]:
        for outfit in outfits:
            outfit_parts = []
            for item in outfit.get("items", []):
                keyword = item.get("keyword") or item.get("name", "")
                outfit_parts.append(item.get("name", keyword))
                item["links"] = {
                    "淘宝搜索": f"https://s.taobao.com/search?q={quote_plus(keyword)}",
                    "京东搜索": f"https://search.jd.com/Search?keyword={quote_plus(keyword)}",
                    "1688搜索": f"https://s.1688.com/selloffer/offer_search.htm?keywords={quote_plus(keyword)}",
                }
                item["image_url"] = self._image_url(
                    f"single clothing product photo, {item.get('type', '')}, {item.get('name', '')}, "
                    "clean white background, fashion catalog, no text, no logo"
                )

            prompt = (
                "full body kpop dance stage outfit flat lay collage, "
                f"{outfit.get('name', '')}, {outfit.get('image_query', '')}, "
                f"items: {', '.join(outfit_parts)}, shoes and accessories included, "
                "fashion editorial, clean background, no text, no logo"
            )
            outfit["image_url"] = self._image_url(prompt, width=900, height=1200)
        return sorted(outfits, key=lambda outfit: outfit.get("total_price", 0))

    def _image_url(self, prompt: str, width: int = 640, height: int = 640) -> str:
        encoded = quote_plus(prompt[:900])
        return (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width={width}&height={height}&nologo=true&enhance=true&model=flux"
        )
