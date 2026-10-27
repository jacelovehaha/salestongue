"""Kit generation from industry packs.

A pack is a JSON file of field-tested talk patterns for one trade
(hooks, angles, CTAs, livestream lines, Q&A). Templates use {product},
{brand}, {slogan}, {price} and {point} placeholders. Generation is
template composition with a seeded RNG — same input, same kit — so a
merchant can regenerate, diff and version their talk tracks like code.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path

PACKS_DIR = Path(__file__).parent / "packs"


@dataclass
class ProductInfo:
    product: str
    brand: str
    slogan: str = ""
    price: str = ""
    points: list[str] = field(default_factory=list)  # selling points


def list_packs() -> list[str]:
    return sorted(p.stem for p in PACKS_DIR.glob("*.json"))


def load_pack(industry: str) -> dict:
    path = PACKS_DIR / f"{industry}.json"
    if not path.exists():
        raise ValueError(f"unknown industry pack {industry!r}; "
                         f"available: {', '.join(list_packs())}")
    return json.loads(path.read_text(encoding="utf-8"))


class _Filler:
    def __init__(self, info: ProductInfo, rng: random.Random):
        self.info = info
        self.rng = rng
        self._points = list(info.points) or ["现货充足"]
        self._pi = 0

    def fill(self, template: str) -> str:
        point = self._points[self._pi % len(self._points)]
        self._pi += 1
        return (template
                .replace("{product}", self.info.product)
                .replace("{brand}", self.info.brand)
                .replace("{slogan}", self.info.slogan or self.info.brand)
                .replace("{price}", self.info.price or "私聊询价")
                .replace("{point}", point))


def build_kit(info: ProductInfo, industry: str, seed: int = 42) -> dict:
    pack = load_pack(industry)
    rng = random.Random(seed)
    f = _Filler(info, rng)

    hooks = rng.sample(pack["hooks"], k=min(3, len(pack["hooks"])))
    angles = rng.sample(pack["angles"], k=min(3, len(pack["angles"])))
    scripts = []
    points = info.points or ["现货充足"]
    for i, (hook, angle) in enumerate(zip(hooks, angles), start=1):
        cta = f.fill(rng.choice(pack["cta"]))
        scripts.append({
            "title": f"脚本{i}：{f.fill(angle)[:18]}",
            "hook": f.fill(hook),
            "body": [
                f.fill(angle),
                f"卖点：{points[(i - 1) % len(points)]}，{info.product}都是实拍实测，不玩虚的。",
                f"价格：{f.fill('{price}')}，这个价只在{info.brand}。",
            ],
            "cta": cta,
        })

    kit = {
        "product": info.product,
        "brand": info.brand,
        "industry": pack["label"],
        "scripts": scripts,
        "livestream": {
            "opener": f.fill(rng.choice(pack["live_openers"])),
            "push": [f.fill(x) for x in rng.sample(pack["live_push"],
                                                   k=min(3, len(pack["live_push"])))],
        },
        "qa": [{"q": qa["q"], "a": f.fill(qa["a"])} for qa in pack["qa"]],
        "poster": [f.fill(x) for x in rng.sample(pack["poster"],
                                                 k=min(3, len(pack["poster"])))],
    }
    return kit


def render_markdown(kit: dict) -> str:
    out = [f"# {kit['brand']} · {kit['product']} 销售话术包", "",
           f"行业：{kit['industry']}", "", "## 短视频脚本", ""]
    for s in kit["scripts"]:
        out += [f"### {s['title']}", f"- 开场钩子：{s['hook']}"]
        out += [f"- {line}" for line in s["body"]]
        out += [f"- 结尾引导：{s['cta']}", ""]
    lv = kit["livestream"]
    out += ["## 直播话术", "", f"开场：{lv['opener']}", ""]
    out += [f"- {line}" for line in lv["push"]]
    out += ["", "## 客户常见问题", ""]
    for qa in kit["qa"]:
        out += [f"**问：{qa['q']}**", f"答：{qa['a']}", ""]
    out += ["## 首图/海报文案", ""]
    out += [f"- {line}" for line in kit["poster"]]
    out += ["", "— 由 salestongue 生成，可自由修改使用。"]
    return "\n".join(out)
