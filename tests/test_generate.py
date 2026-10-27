import io
import unittest
from contextlib import redirect_stdout

from salestongue.cli import main
from salestongue.generate import ProductInfo, build_kit, list_packs, load_pack

INFO = ProductInfo(
    product="库存棉布", brand="晓威库存布", slogan="买库存布找晓威库存布",
    price="3元/米起", points=["现货多", "花色全", "价格低"],
)


class TestPacks(unittest.TestCase):
    def test_four_packs(self):
        self.assertEqual(list_packs(), ["clothing", "fabric", "furniture", "general"])

    def test_pack_shape(self):
        for name in list_packs():
            pack = load_pack(name)
            for key in ("label", "hooks", "angles", "cta", "live_openers",
                        "live_push", "qa", "poster"):
                self.assertIn(key, pack, f"{name}:{key}")
            self.assertGreaterEqual(len(pack["qa"]), 5)

    def test_unknown_pack_raises(self):
        with self.assertRaises(ValueError):
            load_pack("spaceships")


class TestKit(unittest.TestCase):
    def setUp(self):
        self.kit = build_kit(INFO, "fabric")

    def test_brand_and_slogan_present(self):
        blob = str(self.kit)
        self.assertIn("晓威库存布", blob)
        self.assertIn("买库存布找晓威库存布", blob)
        self.assertIn("库存棉布", blob)

    def test_three_scripts_with_cta(self):
        self.assertEqual(len(self.kit["scripts"]), 3)
        for s in self.kit["scripts"]:
            self.assertTrue(s["hook"])
            self.assertTrue(s["body"])
            self.assertTrue(s["cta"])

    def test_qa_and_poster(self):
        self.assertEqual(len(self.kit["qa"]), 5)
        self.assertEqual(len(self.kit["poster"]), 3)
        for qa in self.kit["qa"]:
            self.assertNotIn("{", qa["a"])  # all placeholders filled

    def test_deterministic(self):
        self.assertEqual(build_kit(INFO, "fabric"), build_kit(INFO, "fabric"))

    def test_seed_changes_output(self):
        self.assertNotEqual(build_kit(INFO, "fabric", seed=1),
                            build_kit(INFO, "fabric", seed=2))


class TestCli(unittest.TestCase):
    def run_cli(self, argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(argv)
        return code, buf.getvalue()

    def test_packs_command(self):
        code, out = self.run_cli(["packs"])
        self.assertEqual(code, 0)
        self.assertIn("fabric", out)

    def test_make_command(self):
        code, out = self.run_cli([
            "make", "--industry", "furniture", "--product", "真皮沙发",
            "--brand", "老周家具", "--price", "出厂价直降2000",
        ])
        self.assertEqual(code, 0)
        self.assertIn("老周家具", out)
        self.assertIn("短视频脚本", out)


if __name__ == "__main__":
    unittest.main()
