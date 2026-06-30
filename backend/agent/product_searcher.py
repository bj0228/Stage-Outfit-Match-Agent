from urllib.parse import quote_plus


class ProductSearcher:
    def enrich_items(self, outfits: list[dict]) -> list[dict]:
        for outfit in outfits:
            for item in outfit.get("items", []):
                keyword = item.get("keyword") or item.get("name", "")
                item["links"] = {
                    "淘宝": f"https://s.taobao.com/search?q={quote_plus(keyword)}",
                    "京东": f"https://search.jd.com/Search?keyword={quote_plus(keyword)}",
                    "拼多多": f"https://mobile.yangkeduo.com/search_result.html?search_key={quote_plus(keyword)}",
                }
            query = quote_plus(outfit.get("image_query", outfit.get("name", "kpop stage outfit")))
            outfit["image_url"] = f"https://source.unsplash.com/900x1200/?{query}"
        return sorted(outfits, key=lambda outfit: outfit.get("total_price", 0))
