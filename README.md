
<div align="center">
  <img src="assets/logo.png" alt="PaDELXARFF Logo" width="400" />
  <p><strong>A simple tool to generate PubChem fingerprints with PaDEL-Descriptor & create Weka-compatible ARFF files.</strong></p>
</div>
<center>
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![PaDEL](https://img.shields.io/badge/PaDEL--Descriptor-PubChem%20FP-1a73e8?style=flat-square)
![Weka](https://img.shields.io/badge/Weka-ARFF%20Ready-2e7d32?style=flat-square)
![License](https://img.shields.io/badge/License-All%20Rights%20Reserved-0d1b2a?style=flat-square)
</center>
</div>

---

## 📖 Overview

**PaDELXARFF** is a Streamlit web app that takes a bioactivity CSV file (containing molecule IDs, SMILES strings, and class labels), computes **PubChem fingerprints** using PaDEL-Descriptor, and packages everything into a `.arff` file ready for machine-learning workflows in **Weka**.


---

## ⚙️ How It Works

<table>
<tr>
<td align="center"><b>📂</b><br/><sub>STEP 1</sub><br/><b>Upload CSV</b><br/><sub>Drop your bioactivity file<br/>with ID, SMILES & Class</sub></td>
<td align="center"><b>🏷️</b><br/><sub>STEP 2</sub><br/><b>Name Relation</b><br/><sub>Set the <code>@relation</code><br/>tag for your ARFF</sub></td>
<td align="center"><b>🔬</b><br/><sub>STEP 3</sub><br/><b>PaDEL Settings</b><br/><sub>Toggle salt removal,<br/>aromaticity & tautomers</sub></td>
<td align="center"><b>🗂️</b><br/><sub>STEP 4</sub><br/><b>Class Labels</b><br/><sub>Map 1/0 → active/inactive<br/>or keep originals</sub></td>
<td align="center"><b>⬇️</b><br/><sub>OUTPUT</sub><br/><b>Download ARFF</b><br/><sub>One-click download of<br/>your Weka-ready file</sub></td>
</tr>
</table>

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Java 8+

### Install dependencies

```bash
pip install streamlit pandas padelpy
```

### Run the app

```bash
streamlit run PaDELxARFF.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 🔧 PaDEL-Descriptor Options

| Option | Default | Description |
|--------|---------|-------------|
| Remove salt | ✅ On | Strips salt fragments from multi-component structures |
| Detect aromaticity | ✅ On | Assigns aromaticity before descriptor calculation |
| Standardize tautomers | ✅ On | Converts structures to a canonical tautomeric form |
| Standardize nitro groups | ✅ On | Normalises nitro group representation |
| Standardize molecules | ✅ On | General molecular standardization pass |
| SMIRKS tautomers file | None | Optional custom tautomer rules (`.txt` / `.tsv` / `.smirks`) |

---

## 📄 Output ARFF Structure

The generated file follows the standard Weka ARFF format like this:

```
@relation relation_name

@attribute PubchemFP0 numeric
@attribute PubchemFP1 numeric
...
@attribute PubchemFP880 numeric
@attribute class {active, inactive}

@data
0,1,0,1,...,active
1,0,1,0,...,inactive
```

> ✅ **881 PubChem fingerprint bits** are extracted per molecule & written as numeric attributes.

---

## ⚠️ Notes & Limitations

> ⚠️ If PaDEL fails to process a molecule (e.g. invalid SMILES), it is silently skipped. The app will warn you if the output row count differs from the input and will match by order.

- Processing time scales with the number of compounds — large datasets (1 000+) may take several minutes.
- Java must be installed and accessible on your system `PATH` for PaDEL to run.
- The `@relation` name must not contain spaces (use underscores instead).
- Class label mapping (`1→active`, `0→inactive`) only works for binary integer labels.


<div align="center">
  <img src="assets/footer.png" alt="PaDELXARFF Footer" width="100%" />
</div>

