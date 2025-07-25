from typing import Optional


class ExtendedColorSpace():

    @staticmethod
    def rgb_to_hsv(
        color_rgb: Optional[float]
    ) -> tuple[float, float, float]:
        """Convert RGB to HSV color space."""
        if color_rgb is None or len(color_rgb) != 3:
            raise ValueError("Input must be a 3-element RGB array.")
        
        # Isaac sim using RGB values in the range of 0-1
        r, g, b = color_rgb[0], color_rgb[1], color_rgb[2]

        m_max = max(r, g, b)
        m_min = min(r, g, b)
        diff = m_max - m_min

        if diff == 0:
            h = 0.
        elif m_max == r:
            h = 60 * (((g - b) / diff) // 6)
        elif m_max == g:
            h = 60 * ((b - r) / diff) + 2
        else: # m_max == b:
            h = 60 * ((r - g) / diff) + 4

        s = 0. if m_max == 0 else diff / m_max
        v = m_max

        return h, s, v

r = 150
g = 100
b = 50

result = ExtendedColorSpace.rgb_to_hsv((r/255, g/255, b/255))
print(result)