import requests
import pandas as pd

BOLD = lambda x: f"**{x}**"
MONEY = lambda x: f"${x:,.2f}"
RED = lambda x: f"<font color='red'>{x}</red>"
GREEN = lambda x: f"<font color='green'>{x}</font>"
GREY = lambda x: f"<font color='grey'>{x}</grey>"

HORIZONTAL_LINE_ELEMENT = {"tag": "hr"}


class LarkClient:
    def __init__(self, key):
        self.url = "https://open.larksuite.com/open-apis/bot/v2/hook/{}".format(key)

    def send_card(
        self,
        header: dict = None,
        elements: dict = None,
        df: pd.DataFrame = None,
        header_formatters: dict = None,
        row_elem_formatters: dict = None,
    ):
        elements = elements or [
            self.generate_table_element(
                df,
                header_formatters=header_formatters,
                row_elem_formatters=row_elem_formatters,
            )
        ]
        data = {"msg_type": "interactive", "card": {"elements": elements}}
        if header:
            data["card"]["header"] = header
        resp = requests.post(url=self.url, json=data)
        return resp

    @staticmethod
    def generate_header_element(content: str, color: str):
        return {"title": {"tag": "markdown", "content": content}, "template": color}

    @staticmethod
    def generate_markdown_element(content: str):
        return {
            "tag": "markdown",
            "content": content,
        }

    @staticmethod
    def generate_table_element(
        df: pd.DataFrame,
        header_formatters: dict = None,
        row_elem_formatters: dict = None,
    ) -> dict:
        if df.empty:
            return None

        default_header_formatter = BOLD
        default_row_elem_formatter = str

        columns = []
        header_formatters = header_formatters or {}
        row_elem_formatters = row_elem_formatters or {}

        for col in df.columns:
            header_formatter = header_formatters.get(col, default_header_formatter)
            row_elem_formatter = row_elem_formatters.get(
                col, default_row_elem_formatter
            )

            header = header_formatter(col)
            column_elements = [row_elem_formatter(e) for e in df[col]]

            columns.append(
                {
                    "tag": "column",
                    # "width": "auto",
                    "width": "weighted",
                    "weight": 1,
                    "elements": [
                        {
                            "tag": "markdown",
                            "content": "\n".join([header, *column_elements]),
                        }
                    ],
                }
            )

        return {
            "tag": "column_set",
            "flex_mode": "none",
            "background_style": "default",
            "horizontal_spacing": "default",
            "columns": columns,
        }
