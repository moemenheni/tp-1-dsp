"""Solution executable for TP1 DSP: YUV 4:2:0 memory addressing."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Plane(str, Enum):
    """The three planes of a planar YUV 4:2:0 image."""

    Y = "Y"
    U = "U"
    V = "V"


@dataclass(frozen=True)
class Yuv420Layout:
    """Memory layout for one or more contiguous planar YUV 4:2:0 frames."""

    width: int = 352
    height: int = 288
    y_base: int = 0x00EC470
    u_base: int = 0x00105070
    v_base: int = 0x0010B370

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")
        if self.width % 2 or self.height % 2:
            raise ValueError("YUV 4:2:0 requires even dimensions")
        if min(self.y_base, self.u_base, self.v_base) < 0:
            raise ValueError("base addresses must be non-negative")

    @property
    def chroma_width(self) -> int:
        return self.width // 2

    @property
    def chroma_height(self) -> int:
        return self.height // 2

    @property
    def y_plane_size(self) -> int:
        return self.width * self.height

    @property
    def chroma_plane_size(self) -> int:
        return self.chroma_width * self.chroma_height

    @property
    def frame_size(self) -> int:
        return self.y_plane_size + 2 * self.chroma_plane_size

    def address(
        self, frame: int, x: int, y: int, plane: Plane | str
    ) -> int:
        """Return the byte address of pixel (x, y) in a contiguous frame buffer.

        Chroma coordinates use integer division by two, as required by 4:2:0.
        The frame number is applied when complete frames are stored contiguously.
        """

        if frame < 0:
            raise ValueError("frame must be non-negative")
        if not 0 <= x < self.width or not 0 <= y < self.height:
            raise ValueError(
                f"pixel ({x}, {y}) is outside {self.width}x{self.height}"
            )
        try:
            selected_plane = Plane(plane)
        except ValueError as exc:
            raise ValueError("plane must be Y, U, or V") from exc

        frame_offset = frame * self.frame_size
        if selected_plane is Plane.Y:
            return self.y_base + frame_offset + y * self.width + x

        chroma_offset = (y // 2) * self.chroma_width + (x // 2)
        base = self.u_base if selected_plane is Plane.U else self.v_base
        return base + frame_offset + chroma_offset

    def addresses(self, frame: int, x: int, y: int) -> dict[Plane, int]:
        """Return the addresses of Y, U and V for one luma coordinate."""

        return {
            plane: self.address(frame, x, y, plane)
            for plane in Plane
        }


def copy_yuv420_frame(
    source: bytes | bytearray | memoryview,
    destination: bytearray,
    width: int = 352,
    height: int = 288,
) -> None:
    """Copy one planar YUV 4:2:0 frame, plane by plane, like the TP's C code."""

    layout = Yuv420Layout(width=width, height=height)
    if len(source) < layout.frame_size:
        raise ValueError("source is smaller than one YUV 4:2:0 frame")
    if len(destination) < layout.frame_size:
        raise ValueError("destination is smaller than one YUV 4:2:0 frame")

    y_end = layout.y_plane_size
    u_end = y_end + layout.chroma_plane_size
    destination[:y_end] = source[:y_end]
    destination[y_end:u_end] = source[y_end:u_end]
    destination[u_end:layout.frame_size] = source[u_end:layout.frame_size]


def format_address(address: int) -> str:
    """Format an address using the notation used in the assignment."""

    return f"0x{address:06x}"


if __name__ == "__main__":
    layout = Yuv420Layout()
    for frame, x, y in ((0, 45, 120), (7, 200, 60)):
        print(f"frame {frame}, point ({x}, {y})")
        for plane, address in layout.addresses(frame, x, y).items():
            print(f"  {plane.value}: {format_address(address)}")
