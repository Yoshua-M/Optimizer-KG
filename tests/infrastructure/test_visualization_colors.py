import unittest

from optimizer.infrastructure.visualization.colors import (
    HEATMAP_COLOR_HIGH,
    HEATMAP_COLOR_LOW,
    gradient_color,
    metric_gradient_color,
    relevance_gradient_color,
    value_gradient_color,
)


class VisualizationColorsTests(unittest.TestCase):
    def test_relevance_gradient_endpoints(self):
        self.assertEqual(relevance_gradient_color(0.0), HEATMAP_COLOR_LOW)
        self.assertEqual(relevance_gradient_color(1.0), HEATMAP_COLOR_HIGH)

    def test_value_gradient_endpoints(self):
        self.assertEqual(value_gradient_color(0.0), "#4A3728")
        self.assertEqual(value_gradient_color(1.0), "#2196F3")

    def test_metric_gradient_endpoints(self):
        self.assertEqual(metric_gradient_color(0.0), "#9E9E9E")
        self.assertEqual(metric_gradient_color(1.0), "#2196F3")

    def test_gradient_clamps_out_of_range(self):
        low = gradient_color("relevance", -0.5)
        high = gradient_color("relevance", 1.5)
        self.assertEqual(low, HEATMAP_COLOR_LOW)
        self.assertEqual(high, HEATMAP_COLOR_HIGH)

    def test_midpoint_is_interpolated(self):
        mid = relevance_gradient_color(0.5)
        self.assertNotEqual(mid, HEATMAP_COLOR_LOW)
        self.assertNotEqual(mid, HEATMAP_COLOR_HIGH)


if __name__ == "__main__":
    unittest.main()
