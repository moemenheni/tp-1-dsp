import unittest

from src.tp1_dsp import Plane, Yuv420Layout, copy_yuv420_frame


class Yuv420AddressTests(unittest.TestCase):
    def setUp(self) -> None:
        self.layout = Yuv420Layout()

    def test_frame_zero_requested_point(self) -> None:
        self.assertEqual(
            self.layout.addresses(0, 45, 120),
            {
                Plane.Y: 0x0F699D,
                Plane.U: 0x1079C6,
                Plane.V: 0x10DCC6,
            },
        )

    def test_frame_seven_requested_point(self) -> None:
        self.assertEqual(
            self.layout.addresses(7, 200, 60),
            {
                Plane.Y: 0x1F55B8,
                Plane.U: 0x20A374,
                Plane.V: 0x210674,
            },
        )

    def test_chroma_uses_subsampled_coordinates(self) -> None:
        self.assertEqual(self.layout.address(0, 45, 120, Plane.U), 0x1079C6)
        self.assertEqual(self.layout.address(0, 44, 121, Plane.U), 0x1079C6)

    def test_invalid_coordinates_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.layout.address(0, 352, 0, Plane.Y)
        with self.assertRaises(ValueError):
            self.layout.address(0, 0, 288, Plane.Y)
        with self.assertRaises(ValueError):
            self.layout.address(-1, 0, 0, Plane.Y)


class Yuv420CopyTests(unittest.TestCase):
    def test_copy_preserves_all_three_planes(self) -> None:
        layout = Yuv420Layout(width=4, height=4)
        source = bytes(range(layout.frame_size))
        destination = bytearray([255] * layout.frame_size)

        copy_yuv420_frame(source, destination, width=4, height=4)

        self.assertEqual(destination, source)

    def test_copy_rejects_short_buffers(self) -> None:
        with self.assertRaises(ValueError):
            copy_yuv420_frame(b"\x00", bytearray(24), width=4, height=4)
        with self.assertRaises(ValueError):
            copy_yuv420_frame(bytes(24), bytearray(1), width=4, height=4)


if __name__ == "__main__":
    unittest.main()
