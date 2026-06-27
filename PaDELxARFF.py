import streamlit as st
import pandas as pd
import tempfile
import os
import io
import time
from padelpy import padeldescriptor

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PaDELxARFF",
    layout="centered",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .arff {
        color: #000000;
    }
    .ify {
        color: #1a73e8;
    }
    .subtitle {
        color: #666;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .step-card {
        background: #f8f9fa;
        border-left: 4px solid #1a73e8;
        border-radius: 6px;
        padding: 0.8rem 1rem;
        margin-bottom: 1rem;
    }
    .step-label {
        font-weight: 600;
        color: #1a73e8;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .success-box {
        background: #e8f5e9;
        border-left: 4px solid #2e7d32;
        border-radius: 6px;
        padding: 0.8rem 1rem;
    }
    .warn-box {
        background: #fff8e1;
        border-left: 4px solid #f9a825;
        border-radius: 6px;
        padding: 0.8rem 1rem;
    }
    .settings-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.5rem;
    }
    .footer-bar {
        background: linear-gradient(90deg, #0d1b2a 0%, #1a3a5c 100%);
        border-radius: 10px;
        padding: 1rem 1.5rem;
        margin-top: 1.5rem;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 0.5rem;
    }
    .footer-brand {
        font-size: 1.15rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: 0.5px;
    }
    .footer-brand span {
        color: #4da6ff;
    }
    .footer-meta {
        font-size: 0.78rem;
        color: #a0b8cc;
        text-align: right;
        line-height: 1.6;
    }
    .footer-meta a {
        color: #4da6ff;
        text-decoration: none;
        font-weight: 600;
    }
    .footer-meta a:hover {
        text-decoration: underline;
    }
    .footer-stack {
        font-size: 0.72rem;
        color: #6a8a9e;
        margin-top: 0.15rem;
    }
    .footer-copy {
        font-size: 0.70rem;
        color: #4a6a7e;
        margin-top: 0.1rem;
    }

</style>

""", unsafe_allow_html=True)

st.markdown(
    """
    <div class="main-title">
        <span class="arff">PaDEL</span><span class="ify">xARFF</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">A simple tool to generate PubChem fingerprints with PaDEL-Descriptor & create Weka-compatible ARFF files.</div>',
    unsafe_allow_html=True
)
st.divider()

# ─── STEP 1: Upload CSV ────────────────────────────────────────────────────────
st.markdown('<div class="step-card"><div class="step-label">Step 1 · Upload bioactivity CSV</div></div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "CSV must contain: **ID**, **SMILES**, **Class** columns",
    type=["csv"],
    help="Expected format: ID (molecule identifier), SMILES (structure), Class (e.g. 1/0 or active/inactive)"
)

df_input = None
if uploaded_file:
    try:
        df_input = pd.read_csv(uploaded_file)
        required = {"ID", "SMILES", "Class"}
        missing = required - set(df_input.columns)
        if missing:
            st.error(f"❌ Missing required columns: **{', '.join(missing)}**\n\nFound columns: {list(df_input.columns)}")
            df_input = None
        else:
            st.success(f"✅ Loaded **{len(df_input):,}** compounds · Columns: {list(df_input.columns)}")
            with st.expander("Preview data (first 5 rows)"):
                st.dataframe(df_input.head(), use_container_width=True)

            # Class mapping preview
            unique_classes = df_input["Class"].unique().tolist()
            st.markdown(f"**Class values detected:** `{unique_classes}`")
    except Exception as e:
        st.error(f"❌ Could not read file: {e}")

st.divider()

# ─── STEP 2: Relation name ─────────────────────────────────────────────────────
st.markdown('<div class="step-card"><div class="step-label">Step 2 · Set ARFF @relation name</div></div>', unsafe_allow_html=True)

relation_name = st.text_input(
    "@relation name",
    placeholder="e.g. CDK5_pubchem",
    help="This becomes the @relation tag at the top of the ARFF file"
)

if relation_name:
    st.code(f"@relation {relation_name}", language="text")

st.divider()

# ─── STEP 3: PaDEL settings ────────────────────────────────────────────────────
st.markdown('<div class="step-card"><div class="step-label">Step 3 · PaDEL-Descriptor settings</div></div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    opt_removesalt        = st.checkbox("Remove Salt",              value=True)
    opt_detectarom        = st.checkbox("Detect Dromaticity",       value=True)
    opt_standardizetauto  = st.checkbox("Standardize Tautomers",    value=True)
with col2:
    opt_standardizenitro  = st.checkbox("Standardize Nitro Groups", value=True)
    opt_standardize       = st.checkbox("Standardize Molecules",    value=True)

tautomer_file = st.file_uploader(
    "Upload SMIRKS Tautomers File (optional)",
    type=["txt", "tsv", "smirks"],
    help="Upload a custom SMIRKS tautomers file. If not provided, PaDEL uses its built-in rules."
)

st.divider()

# ─── STEP 4: Class label mapping ──────────────────────────────────────────────
st.markdown('<div class="step-card"><div class="step-label">Step 4 · Class label mapping</div></div>', unsafe_allow_html=True)

class_mode = st.radio(
    "How should class values appear in ARFF?",
    options=["1 (active), 0 (inactive)", "Keep Original Values"],
    horizontal=True,
)
use_active_inactive = class_mode.startswith("active")

st.divider()

# ─── GENERATE BUTTON ───────────────────────────────────────────────────────────
ready = df_input is not None and bool(relation_name.strip())

if not ready:
    st.info("⬆️ Complete Steps 1 and 2 to enable generation.")

generate_btn = st.button(
    "⚙️  Generate PubChem Fingerprints & Build ARFF",
    disabled=not ready,
    use_container_width=True,
    type="primary",
)

if generate_btn and ready:
    with st.status("Processing…", expanded=True) as status:

        # ── Write SMILES to temp dir ──────────────────────────────────────────
        st.write("📁 Preparing molecule files…")
        tmpdir = tempfile.mkdtemp()
        smi_path = os.path.join(tmpdir, "molecules.smi")
        out_csv  = os.path.join(tmpdir, "fingerprints.csv")

        # Write ID  SMILES  (PaDEL uses tab-sep .smi)
        with open(smi_path, "w") as f:
            for _, row in df_input.iterrows():
                f.write(f"{row['SMILES']}\t{row['ID']}\n")

        # Handle optional tautomer file
        tau_path = None
        if tautomer_file is not None:
            tau_path = os.path.join(tmpdir, "tautomers.txt")
            with open(tau_path, "wb") as tf:
                tf.write(tautomer_file.read())

        # ── Run PaDEL-Descriptor ─────────────────────────────────────────────
        st.write("🔬 Running PaDEL-Descriptor (PubChem fingerprints)…")
        t0 = time.time()
        try:
            padeldescriptor(
                mol_dir=smi_path,
                d_file=out_csv,
                fingerprints=True,
                detectaromaticity=opt_detectarom,
                removesalt=opt_removesalt,
                standardizenitro=opt_standardizenitro,
                standardizetautomers=opt_standardizetauto,
                tautomerlist=tau_path,
                retainorder=True,
                threads=-1,
                d_2d=False,
                d_3d=False,
                headless=True,
            )
        except Exception as e:
            st.error(f"❌ PaDEL-Descriptor failed: {e}")
            st.stop()

        elapsed = time.time() - t0
        st.write(f"✅ PaDEL finished in {elapsed:.1f}s")

        # ── Load fingerprint CSV ─────────────────────────────────────────────
        st.write("📊 Loading fingerprint data…")
        df_fp = pd.read_csv(out_csv)

        # Extract only PubchemFP columns
        pubchem_cols = [c for c in df_fp.columns if c.startswith("PubchemFP")]
        st.write(f"   → {len(pubchem_cols)} PubChem fingerprint bits extracted")

        # Merge with original Class labels (by order, retainorder=True)
        df_fp = df_fp.reset_index(drop=True)
        df_original = df_input.reset_index(drop=True)

        # Handle size mismatch (failed molecules)
        if len(df_fp) != len(df_original):
            st.warning(
                f"⚠️ PaDEL returned {len(df_fp)} rows but input had {len(df_original)}. "
                "Some molecules may have failed. Matching by order."
            )
            n = min(len(df_fp), len(df_original))
            df_fp = df_fp.iloc[:n]
            df_original = df_original.iloc[:n]

        df_fp["Class"] = df_original["Class"].values

        # Apply class label mapping
        if use_active_inactive:
            df_fp["Class"] = df_fp["Class"].map({1: "active", 0: "inactive"}).fillna(df_fp["Class"].astype(str))
            class_values = ["active", "inactive"]
        else:
            class_values = sorted(df_fp["Class"].astype(str).unique().tolist())

        # ── Build ARFF ───────────────────────────────────────────────────────
        st.write("📝 Building ARFF file…")
        arff_lines = []
        arff_lines.append(f"@relation {relation_name.strip()}")
        arff_lines.append("")

        # Attributes: all PubChem FP columns
        for col in pubchem_cols:
            arff_lines.append(f"@attribute {col} numeric")

        # Class attribute
        class_str = "{" + ", ".join(class_values) + "}"
        arff_lines.append(f"@attribute class {class_str}")
        arff_lines.append("")
        arff_lines.append("@data")

        # Data rows
        for _, row in df_fp.iterrows():
            fp_vals = ",".join(str(int(row[c])) for c in pubchem_cols)
            cls_val = str(row["Class"])
            arff_lines.append(f"{fp_vals},{cls_val}")

        arff_content = "\n".join(arff_lines)

        status.update(label="✅ Done!", state="complete", expanded=False)

    # ── Results summary ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📋 Results Summary")

    c1, c2, c3 = st.columns(3)
    c1.metric("Compounds", f"{len(df_fp):,}")
    c2.metric("FP bits", f"{len(pubchem_cols)}")
    c3.metric("Class labels", ", ".join(str(v) for v in class_values))

    with st.expander("Preview ARFF (first 30 lines)"):
        preview = "\n".join(arff_lines[:30])
        st.code(preview, language="text")

    # ── Download ──────────────────────────────────────────────────────────────
    arff_bytes = arff_content.encode("utf-8")
    filename   = f"{relation_name.strip().replace(' ', '_')}.arff"

    st.download_button(
        label="⬇️  Download ARFF File",
        data=arff_bytes,
        file_name=filename,
        mime="text/plain",
        use_container_width=True,
        type="primary",
    )

    st.markdown(
        f'<div class="success-box">🎉 <b>{filename}</b> is ready — {len(arff_bytes)/1024:.1f} KB</div>',
        unsafe_allow_html=True
    )

# ─── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div class="footer-bar">
    <div class="footer-brand">🧪 PaDEL<span>xARFF</span></div>
    <div class="footer-meta">
        Designed &amp; developed by <a href="https://www.linkedin.com/in/nabiulorko" target="_blank">Nabiul Orko</a><br>
        <span class="footer-stack">PaDEL-Descriptor · PubChem FP · Python · Streamlit</span><br>
        <span class="footer-copy">© 2026 All Rights Reserved</span>
    </div>
</div>
""", unsafe_allow_html=True)
