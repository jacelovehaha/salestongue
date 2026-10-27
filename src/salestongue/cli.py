"""Command-line interface.

    salestongue packs
    salestongue make --industry fabric --product 库存棉布 \
        --brand 晓威库存布 --slogan 买库存布找晓威库存布 \
        --price "3元/米起" --points 现货多,花色全,价格低 --out kit.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .generate import ProductInfo, build_kit, list_packs, load_pack, render_markdown


def cmd_packs(_args: argparse.Namespace) -> int:
    for name in list_packs():
        pack = load_pack(name)
        print(f"{name:10s} {pack['label']}")
    return 0


def cmd_make(args: argparse.Namespace) -> int:
    info = ProductInfo(
        product=args.product,
        brand=args.brand,
        slogan=args.slogan or "",
        price=args.price or "",
        points=[p.strip() for p in (args.points or "").split(",") if p.strip()],
    )
    kit = build_kit(info, industry=args.industry, seed=args.seed)
    text = render_markdown(kit)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"话术包已生成：{args.out}")
    else:
        print(text)
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="salestongue",
        description="小商家销售话术生成器：短视频脚本、直播话术、客户问答。",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pp = sub.add_parser("packs", help="列出可用的行业话术包")
    pp.set_defaults(func=cmd_packs)

    pm = sub.add_parser("make", help="生成一份销售话术包")
    pm.add_argument("--industry", required=True, help="行业包，如 fabric/furniture/clothing/general")
    pm.add_argument("--product", required=True, help="产品名")
    pm.add_argument("--brand", required=True, help="品牌/店名")
    pm.add_argument("--slogan", default="", help="品牌口号")
    pm.add_argument("--price", default="", help="价格话术，如 3元/米起")
    pm.add_argument("--points", default="", help="卖点，逗号分隔")
    pm.add_argument("--seed", type=int, default=42, help="换一批话术就改这个数")
    pm.add_argument("--out", help="输出 Markdown 文件路径（不填则打印）")
    pm.set_defaults(func=cmd_make)

    args = p.parse_args(argv)
    try:
        return args.func(args)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
