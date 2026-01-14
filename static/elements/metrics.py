import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from static.elements.layout import tile

# ---- Design tokens (for now – later these can move to config/theme) ----
primary_background   = "#111111"
secondary_background = "#171717"
dark_text_color      = "#171717"
light_text_color     = "#E8E8E8"
color_1              = "#5A85F3"  # Blue
color_2              = "#CDFFD8"  # Green
border_color         = "#3c3c3c"
caption_color        = "#878884"


def gradient_metric_tile(
    key: str,
    stat: str,
    value: str,
    tooltip: str | None = None,
):
    """
    Metric/KPI tile.

    Example:
        metric_tile(
            key="return",
            stat="Return",
            value="1.10%",
            tooltip="Net return for the current evaluation stage."
        )
    """

    text_color = dark_text_color

    # simple gradient fill container for secondary style
    css_style = f"""
    {{
        background: linear-gradient(135deg, {color_1}, {color_2});
        border-radius: 0.5rem;
        padding: 1em;
        color: {dark_text_color};
        display: flex;
        align-items: flex-start;
        justify-content: flex-start;
    }}
    """

    with stylable_container(key=key, css_styles=css_style):
        with st.container(border=False, height=65):
            st.markdown(
                f"""
                <div style="line-height: 1.5;">
                    <p style="margin: 0; font-size: 0.85em; color: {text_color};">
                        {stat}
                    </p>
                    <p style="margin: 0; font-size: 1.2em; font-weight: bold; color: {text_color};">
                        {value}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
                help=tooltip,
            )

def standard_metric_tile(
    key: str,
    stat: str,
    value: str,
    tooltip: str | None = None,
):
    """
    Metric/KPI tile.

    Example:
        metric_tile(
            key="return",
            stat="Return",
            value="1.10%",
            tooltip="Net return for the current evaluation stage."
        )
    """

    text_color = light_text_color

    with tile(key, 65, True):
        st.markdown(
            f"""
            <div style="line-height: 1.5;">
                <p style="margin: 0; font-size: 0.85em; color: {caption_color};">
                    {stat}
                </p>
                <p style="margin: 0; font-size: 1.2em; font-weight: bold; color: {text_color};">
                    {value}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
            help=tooltip,
        )
