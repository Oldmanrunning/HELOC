"""Backward-compatible launcher for the refactored HELOC Streamlit app.

The original single-file Streamlit app has been reorganized into the `heloc`
package. Run `streamlit run app.py` for the portfolio-ready entrypoint, or run
this file while older bookmarks/deployment settings are updated.
"""

from app import render_app


if __name__ == "__main__":
    render_app()
