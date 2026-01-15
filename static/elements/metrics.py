import streamlit as st

# Keep your existing tokens (single source of truth)
primary_background   = "#111111"
secondary_background = "#171717"
dark_text_color      = "#171717"
light_text_color     = "#E8E8E8"
color_1              = "#5A85F3"  # Blue
color_2              = "#CDFFD8"  # Green
border_color         = "#3c3c3c"
caption_color        = "#878884"


# --------------------------------------------------------------------------------------
# Metric Tile (glassmorphic, dashboard-ready)
# --------------------------------------------------------------------------------------

_GLASS_TILE_CSS_TMPL = """
<style>
div.st-key-{key} {{
    background: rgba(23, 23, 23, 0.55) !important;
    border: 1px solid {border} !important;
    border-radius: 8px;
    padding: 16px;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
}}
</style>
"""


def metric_tile(
    *,
    key: str,
    title: str,
    value: str,
    value_size: str = "1.5rem",
    title_badge: str | None = None,
    title_badge_color: str = "green",
    footer_badge: str | None = None,
    footer_badge_color: str = "green",
    right_label: str | None = None,
    progress: float | None = None,
    height: int = 130,
    tooltip: str | None = None,
    title_padding_bottom: str = "1rem",
):
    """
    Unified metric tile for the dashboard.

    Supports:
      - Title + optional badge (right-aligned in header row)
      - Big value
      - Optional right label (e.g. "of $10,000")
      - Optional progress bar
      - Optional footer badge (e.g. "Active")
    """

    # Inject per-tile CSS (targets Streamlit container class derived from key)
    st.markdown(
        _GLASS_TILE_CSS_TMPL.format(key=key, border=border_color),
        unsafe_allow_html=True,
    )

    with st.container(key=key, border=False, height=height):
        # Header row: title + optional badge
        with st.container(border=False, horizontal=True, vertical_alignment="center"):
            st.markdown(
                f"""
                <div style="
                    font-family: 'Source Sans Pro', 'Source Sans', sans-serif;
                    color: var(--text-color);
                    font-size: 0.875rem;
                    line-height: normal;
                    max-width: 100%;
                    overflow: hidden;
                    white-space: nowrap;
                    text-overflow: ellipsis;
                    margin: 0;
                    padding: 0;
                ">
                    <p style="
                        margin: 0;
                        padding: 0;
                        padding-bottom: {title_padding_bottom};
                        overflow: hidden;
                        text-overflow: ellipsis;
                        color: {caption_color};
                    " title="{title}">{title}</p>
                </div>
                """,
                unsafe_allow_html=True,
                help=tooltip,
            )
            if title_badge:
                st.badge(title_badge, color=title_badge_color)

        # Value + optional right label
        with st.container(border=False, horizontal=True, vertical_alignment="bottom"):
            st.markdown(
                f"""
                <div style="
                    font-family: 'Source Sans Pro', 'Source Sans', sans-serif;
                    color: {light_text_color};
                    width: 100%;
                    overflow: hidden;
                    white-space: nowrap;
                    text-overflow: ellipsis;
                    line-height: normal;
                ">
                    <div style="
                        font-size: {value_size};
                        font-weight: 400;
                        padding-bottom: 0.5rem;
                        line-height: 1.2;
                    ">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if right_label:
                st.space("stretch")
                st.markdown(
                    f"""
                    <div style="
                        font-family: 'Source Sans Pro', 'Source Sans', sans-serif;
                        color: {caption_color};
                        font-size: 0.875rem;
                        line-height: normal;
                        white-space: nowrap;
                        padding-bottom: 0.65rem;
                    ">{right_label}</div>
                    """,
                    unsafe_allow_html=True,
                )

        if progress is not None:
            st.progress(progress)

        if footer_badge:
            st.badge(footer_badge, color=footer_badge_color)
