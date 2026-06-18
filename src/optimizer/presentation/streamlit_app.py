import streamlit as st
import streamlit.components.v1 as components

from optimizer.application.run_pyvis_graph import run_pyvis_graph


def run_app():
    """Render the Streamlit knowledge graph UI."""
    st.title("Knowledge Graph From Text")

    st.sidebar.title("Input document")
    input_method = st.sidebar.radio(
        "Choose an input method:",
        ["Upload txt", "Input text"],
    )

    if input_method == "Upload txt":
        uploaded_file = st.sidebar.file_uploader(label="Upload file", type=["txt"])

        if uploaded_file is not None:
            text = uploaded_file.read().decode("utf-8")

            if st.sidebar.button("Generate Knowledge Graph"):
                with st.spinner("Generating knowledge graph..."):
                    net = run_pyvis_graph(text)
                    st.success("Knowledge graph generated successfully!")

                    output_file = "knowledge_graph.html"
                    net.save_graph(output_file)

                    with open(output_file, "r", encoding="utf-8") as html_file:
                        components.html(html_file.read(), height=1000)
    else:
        text = st.sidebar.text_area("Input text", height=300)

        if text:
            if st.sidebar.button("Generate Knowledge Graph"):
                with st.spinner("Generating knowledge graph..."):
                    net = run_pyvis_graph(text)
                    st.success("Knowledge graph generated successfully!")

                    output_file = "knowledge_graph.html"
                    net.save_graph(output_file)

                    with open(output_file, "r", encoding="utf-8") as html_file:
                        components.html(html_file.read(), height=1000)
