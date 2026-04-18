import os
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sync_engine import generate_thumbnail, optimize_image  # noqa: E402


class TestJpegConversion(unittest.TestCase):
    def test_optimize_image_converts_rgba_png_to_jpeg(self):
        with TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "source.png"
            dest = Path(tmpdir) / "optimized.jpg"

            Image.new("RGBA", (40, 30), (255, 0, 0, 128)).save(src)

            optimize_image(src, dest)

            self.assertTrue(dest.exists())
            with Image.open(dest) as result:
                self.assertEqual(result.format, "JPEG")
                self.assertEqual(result.mode, "RGB")

    def test_generate_thumbnail_converts_palette_png_to_jpeg(self):
        with TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "source.png"
            dest = Path(tmpdir) / "thumb.jpg"

            Image.new("P", (40, 30)).save(src)

            generate_thumbnail(src, dest)

            self.assertTrue(dest.exists())
            with Image.open(dest) as result:
                self.assertEqual(result.format, "JPEG")
                self.assertEqual(result.mode, "RGB")


if __name__ == "__main__":
    unittest.main()
