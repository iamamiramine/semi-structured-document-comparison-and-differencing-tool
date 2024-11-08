# XML Tree Comparison Tool

A command-line tool for comparing XML documents using Nierman-Jagadish or Wagner-Fisher algorithms.

## Dependencies

Required Python packages:
```
lxml
numpy
```

Install using:
```bash
pip install lxml numpy
```

## File Structure

```
.
├── scripts/
│   ├── preprocessing.py  # XML to tree conversion
│   ├── processing.py     # Tree comparison algorithms
│   └── postprocessing.py # Results generation
├── main.py              # Command-line interface
└── README.md
```

## Command-Line Usage

### Single File Comparison
Compare two XML files:
```bash
python main.py --mode single \
    --algorithm nierman \
    --input1 file1.xml \
    --input2 file2.xml \
    --output results/
```

### Dataset Comparison
Compare one file against multiple files:
```bash
python main.py --mode dataset \
    --algorithm wagner \
    --input1 source.xml \
    --dataset xml_files/ \
    --output results/
```

## Command Arguments

| Argument    | Required | Description                           |
|-------------|----------|---------------------------------------|
| --mode      | Yes      | 'single' or 'dataset'                 |
| --algorithm | Yes      | 'nierman' or 'wagner'                 |
| --input1    | Yes      | Path to first/source XML              |
| --input2    | For single| Path to second XML                   |
| --dataset   | For dataset| Directory with XML files            |
| --output    | Yes      | Output directory                      |

## Output Directory Structure

```
results/
├── analysis/
│   ├── comparison_metrics.json  # Performance metrics
│   └── diff_*.txt              # Change reports
└── documents/
    └── output_*.xml            # Result XML files
```

## Algorithms

1. Nierman-Jagadish
   - Structure-focused comparison
   - Ignores text content
   - Use for structural comparisons

2. Wagner-Fisher
   - Includes text comparison
   - Higher accuracy with content
   - Use when text matters

## Example Usage

1. Create output directory:
```bash
mkdir results
```

2. Run comparison:
```bash
python main.py --mode single \
    --algorithm wagner \
    --input1 data/original.xml \
    --input2 data/modified.xml \
    --output results/
```

3. View results:
```bash
cat results/analysis/comparison_metrics.json  # View metrics
cat results/analysis/diff_*.txt              # View changes
```