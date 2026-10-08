# RescU Structural Analysis

Python code for the RescU senior design VTOL fixed-wing UAV's preliminary structural analysis. The model estimates component mass and aircraft center of gravity, battery position, wing spar and VTOL motor-arm stresses and deflections, payload mounting plate loads, and aft structural spine loads.

This is a conceptual/preliminary model. Inputs marked as assumptions need confirmation as CAD, materials, joints, and subsystem locations are finalized.

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
