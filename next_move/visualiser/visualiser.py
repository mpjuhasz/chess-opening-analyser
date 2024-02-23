from plotly import graph_objects as go


class Visualiser:
    def __init__(self):
        pass

    def sankey(self, nodes: dict[str, list], links: dict[str, list], path: str):
        """Sankey visualisation"""
        fig = go.Figure(
            data=[
                go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=nodes["label"],
                    ),
                    link=dict(
                        source=links["source"],
                        target=links["target"],
                        value=links["value"],
                    ),
                )
            ]
        )

        fig.update_layout(title_text="Openings tree", font_size=10)
        fig.write_html(path)

    def timeline(self):
        pass
