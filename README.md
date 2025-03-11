# arXiv2TeX

[![Build Status](https://github.com/rice8y/arXiv2TeX/actions/workflows/CI.yml/badge.svg?branch=main)](https://github.com/rice8y/arXiv2TeX/actions/workflows/CI.yml?query=branch%3Amain)

arXiv2TeX is a Python script that searches for papers on arXiv and outputs a formatted LaTeX table containing the search results. It can be integrated into your workflow for generating summary documents directly from arXiv queries.

## Installation

Clone the repository using:

```bash
git clone https://github.com/rice8y/arXiv2TeX.git
```

## Requirements

- **LaTeX:** A working LaTeX installation is required for compiling the generated .tex file.
- **arxiv:** The Python arXiv module is used to perform the search and retrieve paper metadata.

## Usage

Run the script with your desired query. For example, to search for papers related to "llm" and fetch 30 results, use:

```bash
python3 arxiv2tex.py --query llm --max_results 30
```

The script will generate a LaTeX file (by default arXiv.tex) that contains a table with the selected columns.

### Parameters

- `--query`: The search query string used to find papers on arXiv.
- `--max_results`: The maximum number of search results to fetch. (Default is 10)
- `--sort_by`: The criterion for sorting search results. Options are: relevance, submittedDate, or lastUpdatedDate. (Default is submittedDate)
- `--columns`: A comma-separated list of columns to include in the table. Allowed values are: authors, title, summary, published, and link. (Default is authors,title,published,link)
- `--cls`: The LaTeX document class to use (for example, article, report, etc.). (Default is article)
- `--prefix`: The prefix for the output .tex file. For example, if set to arXiv, the output file will be named arXiv.tex. (Default is arXiv)
- `--mode`: The mode of operation. Use auto for automatic compilation (the script will run the LaTeX compiler) or manual if you prefer to compile the generated .tex file yourself. (Default is auto)
- `--engine`: The LaTeX engine to use for compiling the document. Options include pdflatex, xelatex, lualatex, uplatex, platex, and latex. (Default is lualatex)

## Todo

- [ ] The table format of summary is corrupted.

## License

This package is distributed under the MIT License. See [LICENSE](LICENSE).