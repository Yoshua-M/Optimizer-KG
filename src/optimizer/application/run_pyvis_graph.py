import asyncio

from optimizer.graph_building.extraction import extract_graph_data
from optimizer.infrastructure.visualization.pyvis_graph import visualize_graph


def run_pyvis_graph(text):
    """
    Generates and visualizes a knowledge graph from input text.

    Args:
        text (str): Input text to convert into a knowledge graph.

    Returns:
        pyvis.network.Network: The visualized network graph object.
    """
    graph_documents = asyncio.run(extract_graph_data(text))
    net = visualize_graph(graph_documents)
    return net
