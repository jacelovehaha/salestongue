"""salestongue — sales-talk kits for small merchants.

Turns a product + an industry pack into a ready-to-use kit: short-video
scripts, livestream talk tracks, customer Q&A drafts and poster lines.
Offline and deterministic: no API key, no credits, no upload.
"""

from .generate import ProductInfo, build_kit, list_packs, load_pack

__version__ = "0.1.0"
__all__ = ["ProductInfo", "build_kit", "list_packs", "load_pack", "__version__"]
