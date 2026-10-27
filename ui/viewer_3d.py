"""
ChemLab - 3D Molecular Visualization Component
Integrates py3Dmol with interactive rendering, styles (Ball & Stick, Stick, Spacefill, Wireframe, Cartoon),
CPK element coloring, surface rendering, camera reset, auto-spin, and responsive sizing.
"""

from rdkit import Chem
import py3Dmol
import streamlit.components.v1 as components

def render_3dmol(mol3d, style="Ball and Stick", show_surface=False, height=520, bg_color="#F8FAFC", viewer_id="chemlab_viewer"):
    """
    Render 3D molecular structure using py3Dmol and embed via Streamlit HTML component.
    Includes custom toolbar controls for camera reset and auto-spin directly inside the iframe.
    """
    if mol3d is None or mol3d.GetNumConformers() == 0:
        return

    mol_block = Chem.MolToMolBlock(mol3d)

    view = py3Dmol.view(
        width="100%",
        height=height,
    )
    view.addModel(mol_block, "mol")

    # Configure styles based on selection
    if style == "Ball and Stick":
        view.setStyle({
            "stick": {"radius": 0.15, "color": "spectrum"},
            "sphere": {"scale": 0.28}
        })
    elif style == "Stick":
        view.setStyle({
            "stick": {"radius": 0.22}
        })
    elif style == "Space Filling":
        view.setStyle({
            "sphere": {"scale": 0.95}
        })
    elif style == "Wireframe":
        view.setStyle({
            "line": {"linewidth": 2.2}
        })
    elif style == "Cartoon":
        view.setStyle({
            "stick": {"radius": 0.12},
            "sphere": {"scale": 0.22}
        })
    else:
        view.setStyle({
            "stick": {"radius": 0.15},
            "sphere": {"scale": 0.28}
        })

    # Optional van der Waals surface
    if show_surface:
        view.addSurface(
            py3Dmol.VDW,
            {"opacity": 0.65, "color": "white"}
        )

    # Set viewport background canvas
    view.setBackgroundColor(bg_color)
    view.zoomTo()

    uid = str(view.uniqueid)
    raw_html = view._make_html()

    # Create toolbar script that connects directly to the py3Dmol viewer instance
    toolbar_injection = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; position: relative; width: 100%; border-radius: 8px; overflow: hidden; border: 1px solid #344258; background: #151F33; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.25);">
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 14px; background: #1C2940; border-bottom: 1px solid #344258;">
            <div style="font-size: 12px; font-weight: 600; color: #F1F5F9; display: flex; align-items: center; gap: 8px;">
                <span style="color: #2DD4BF;">🌐</span> <span>Interactive 3D Molecular Viewport</span>
                <span style="background: rgba(125, 211, 252, 0.12); color: #7DD3FC; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; border: 1px solid rgba(125, 211, 252, 0.25);">{style}</span>
            </div>
            <div style="display: flex; gap: 8px;">
                <button type="button" onclick="resetCamera_{uid}()"
                        style="background: #151F33; border: 1px solid #344258; border-radius: 4px; padding: 4px 10px; font-size: 11px; font-weight: 600; color: #F1F5F9; cursor: pointer; transition: all 0.15s ease;"
                        onmouseover="this.style.borderColor='#2DD4BF'; this.style.color='#2DD4BF';"
                        onmouseout="this.style.borderColor='#344258'; this.style.color='#F1F5F9';"
                        title="Reset Camera Orientation & Zoom">
                    🔄 Reset Camera
                </button>
                <button type="button" id="spin_btn_{uid}" onclick="toggleSpin_{uid}()"
                        style="background: #151F33; border: 1px solid #344258; border-radius: 4px; padding: 4px 10px; font-size: 11px; font-weight: 600; color: #F1F5F9; cursor: pointer; transition: all 0.15s ease;"
                        title="Toggle continuous molecular rotation">
                    🌀 Auto-Spin
                </button>
            </div>
        </div>
        {raw_html}
        <script>
        window.activeViewer_{uid} = null;
        window.isSpinning_{uid} = false;

        function getViewer_{uid}() {{
            if (window.activeViewer_{uid}) return window.activeViewer_{uid};
            if (typeof viewer_{uid} !== 'undefined' && viewer_{uid} !== null) {{
                window.activeViewer_{uid} = viewer_{uid};
                return window.activeViewer_{uid};
            }}
            return null;
        }}

        // Attach once $3Dmol initializes
        if (typeof $3Dmolpromise !== 'undefined') {{
            $3Dmolpromise.then(function() {{
                if (typeof viewer_{uid} !== 'undefined') {{
                    window.activeViewer_{uid} = viewer_{uid};
                }}
            }});
        }}

        function resetCamera_{uid}() {{
            var v = getViewer_{uid}();
            if (!v) return;
            // Stop any active spin cleanly
            v.spin(false);
            window.isSpinning_{uid} = false;
            var btn = document.getElementById("spin_btn_{uid}");
            if (btn) {{
                btn.innerHTML = "🌀 Auto-Spin";
                btn.style.color = "#F1F5F9";
                btn.style.borderColor = "#344258";
                btn.style.background = "#151F33";
            }}
            // Reset camera orientation and zoom
            v.zoomTo();
            v.render();
        }}

        function toggleSpin_{uid}() {{
            var v = getViewer_{uid}();
            if (!v) return;
            var btn = document.getElementById("spin_btn_{uid}");
            if (window.isSpinning_{uid}) {{
                v.spin(false);
                window.isSpinning_{uid} = false;
                if (btn) {{
                    btn.innerHTML = "🌀 Auto-Spin";
                    btn.style.color = "#F1F5F9";
                    btn.style.borderColor = "#344258";
                    btn.style.background = "#151F33";
                }}
            }} else {{
                v.spin("y", 1);
                window.isSpinning_{uid} = true;
                if (btn) {{
                    btn.innerHTML = "⏸️ Stop Spin";
                    btn.style.color = "#2DD4BF";
                    btn.style.borderColor = "#2DD4BF";
                    btn.style.background = "rgba(45, 212, 191, 0.15)";
                }}
            }}
        }}
        </script>
    </div>
    """

    components.html(toolbar_injection, height=height + 55)
