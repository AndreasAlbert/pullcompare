# Tools for fit comparisons

## Step 1: Convert nuisance pulls to platform-independnent format

This step separates out the ROOT dependence. Simple use:

```bash
./fitdiag2text.py /path/to/fitDiagnostics.root
```

The output file with created in the same directory as the input


## Step 2: Scatter plot

```bash
python3 nuisance_scatter.py first_fit.json second_fit.json \
                            --fit fit_b \
                            --tags SOME_NAME1,SOME_NAME2  \
                            --style-highlight-threshold 0.5 \
                            --title SOME_TITLE
```
