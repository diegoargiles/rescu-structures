# RescU Structural Analysis

Python code for the RescU senior design VTOL fixed-wing UAV's preliminary structural analysis. The model estimates component mass and aircraft center of gravity, battery position, wing spar and VTOL motor-arm stresses and deflections, payload mounting plate loads, and aft structural spine loads.

This is a conceptual/preliminary model. Inputs marked as assumptions need confirmation as CAD, materials, joints, and subsystem locations are finalized.

## Foam-core candidate (V3)

V3 uses the **confirmed 900 g battery** from the revised report. V2 keeps its historical 650 g input. Current V3 known mass is about **3.650 kg**, sizing mass **3.850 kg**, and the five-ply wing **fails** the 70%-stiffness deflection check. The printed report shows that failure separately from nominal load-case passes. Run `explore_mass_target.py` for the updated 2.76 kg budget and read [mass-target exploration](MASS_TARGET_EXPLORATION.md).

The `foam-core-gfrp` branch adds a separate **preliminary, unresolved** sparless foam/GFRP screening model. V2 remains unchanged. Read [engineering choices and validation limits](DESIGN_NOTES_V3.md) and [the CAD checklist](CAD_REQUEST_V3.md) first. The candidate adds substantial skin mass and does **not** establish compatibility with the current VTOL propulsion budget.

```powershell
python RescU_Structures_V3.py
python -m unittest test_v3 -v
```

Reports and CSV/JSON outputs appear in `results/v3/`, or a folder chosen with `--output`. Generated results are ignored by Git; the code, airfoil data, tests and design notes preserve the reproducible version. No external Python packages are needed. `WING_SKIN`, `TAIL_SKIN`, `FOAMS`, and the visible `SCREEN` assumptions are the main V3 inputs; inherited team geometry/equipment are read from V2. Update the notes when changing an assumption or design choice.

For V3 work in GitHub Desktop, select branch **foam-core-gfrp**, review changes, commit to that branch, then **Push origin**. A commit creates the local checkpoint; a push backs it up to GitHub. Saving the Python file alone does neither. Continue using the original `main` branch for the preserved V2 reference until a replacement is reviewed.

## Run the analysis

Use Python 3.10 or newer. No third-party packages are required.

Open a terminal in `C:\Users\diego\Documents\GitHub\rescu-structures` and run:

```powershell
python RescU_Structures_V2.py
```

The script prints its report and writes these files beside the script, replacing previous outputs with the same names:

- `RescU_Structures_V2_Report.txt`
- `RescU_Structures_V2_Component_Masses.csv`
- `RescU_Structures_V2_Battery_Sweep.csv`

These generated outputs are excluded from Git because they can be regenerated from the code. Other CSV files are not excluded by default.

## Save versions to GitHub

Repository: `diegoargiles/rescu-structures` (private).

Work in the repository folder above so Git can track your edits.

### Optional beginner-friendly workflow: GitHub Desktop

GitHub Desktop is not installed as part of this repository setup. To use it, download it from the [official GitHub Desktop page](https://desktop.github.com/), install it, and sign in to GitHub. Then, once, choose **File > Add local repository** and select `C:\Users\diego\Documents\GitHub\rescu-structures`.

1. Change the code and save the file in your editor.
2. Open GitHub Desktop and select `rescu-structures`.
3. Review the changed files and select the changes you want to save together.
4. Write a short commit message, such as `Update battery position assumptions`, then click **Commit to main**. This records a checkpoint on your computer.
5. Click **Push origin** to upload the committed changes to GitHub.

### Terminal alternative

After editing and saving, open a terminal in the repository folder and run these commands in order:

```powershell
git status
git diff
git add RescU_Structures_V2.py
git commit -m "Update battery position assumptions"
git push
```

Use `git status` and `git diff` to review your changes before committing, and choose a commit message that describes your actual update. Stage `README.md` or other intentionally changed files by name too, for example `git add README.md` before the commit.

Saving a file does not automatically back it up to GitHub. Both a commit and a push are needed. The initial commit records the current script; version history begins with that snapshot. Older edits that were never committed are not recovered automatically.

Before editing from another computer, clone this repository there, then use **Fetch origin** and **Pull origin** when updates are available, or `git pull` in the terminal. On later visits, fetch and pull before editing so you start with the latest pushed version. Review past checkpoints in GitHub Desktop's **History** tab or with `git log --oneline`.
