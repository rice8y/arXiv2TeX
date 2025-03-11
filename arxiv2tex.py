import arxiv
import argparse
import re
import os
import subprocess

ALLOWED_COLUMNS = ["authors", "title", "summary", "published", "link"]

def parse_args():
    parser = argparse.ArgumentParser(description="Search for papers on arXiv and output a LaTeX table.")
    parser.add_argument("--query", type=str, required=True, help="Search query string")
    parser.add_argument("--max_results", type=int, default=10, help="Number of results to fetch")
    parser.add_argument("--sort_by", type=str, choices=["relevance", "submittedDate", "lastUpdatedDate"], default="submittedDate", help="Sorting criterion")
    parser.add_argument("--columns", type=str, default="authors,title,published,link", help="Comma-separated list of columns to display. Allowed: authors, title, summary, published, link")
    parser.add_argument("--prefix", type=str, default="arXiv", help="Prefix for the output .tex file (e.g., 'arXiv' creates arXiv.tex)")
    parser.add_argument("--mode", type=str, choices=["auto", "manual"], default="auto", help="Mode selection: 'auto' for automatic compilation or 'manual'")
    parser.add_argument("--cls", type=str, default="article", help="LaTeX document class to use (e.g., article, report, etc.)")
    parser.add_argument("--engine", type=str, choices=["pdflatex", "xelatex", "lualatex", "uplatex", "platex", "latex"], default="lualatex", help="LaTeX engine to use")
    parser.add_argument("--translate", type=str, default=None, help="Target language for translating paper titles and summaries (e.g., 'ja' for Japanese)")
    parser.add_argument("--service_urls", type=str, nargs="+", default=None, help="List of Google Translate service URLs (e.g., 'translate.google.com translate.google.co.jp')")
    return parser.parse_args()

def escape_latex(s):
    s = s.replace("\\", r"\textbackslash{}")
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}'
    }
    for char, replacement in replacements.items():
        s = s.replace(char, replacement)
    return s

def preamble(lines, args, col):
    cls = args.cls or ("jsarticle" if args.engine in {"uplatex", "platex"} else "article")
    if args.engine in {"uplatex", "platex", "latex"}:
        lines.append(f"\\documentclass[dvipdfmx]{{{cls}}}")
    else:
        lines.append(f"\\documentclass{{{cls}}}")
        
    lines.extend([
        "\\usepackage[hidelinks]{hyperref}",
        "\\usepackage{float}",
        "\\usepackage[margin=1in]{geometry}",
        "\\usepackage{longtable}",
        "\\usepackage{array}",
        "\\newcolumntype{P}[1]{>{\\raggedright\\arraybackslash}p{#1}}",
        "\\newlength\\autolength",
        f"\\setlength\\autolength{{\\dimexpr(\\textwidth - (5\\arrayrulewidth + 8\\tabcolsep)) / {len(col)}\\relax}}"
    ])
    
def get_value(col, r, translator, translate, service_urls):
    if col == "authors":
        return ", ".join([escape_latex(author.name) for author in r.authors])
    elif col == "title":
        if translate:
            return escape_latex(translator(r.title, translate, service_urls))
        else:
            return escape_latex(r.title)
    elif col == "summary":
        if translate:
            return escape_latex(translator(" ".join(r.summary.split()), translate, service_urls))
        else:
            return escape_latex(" ".join(r.summary.split()))
    elif col == "published":
        return escape_latex(str(r.published))
    elif col == "link":
        url = r.links[0].href
        doi_pattern = re.compile(r'https?://(?:dx\.)?doi\.org/10\.\d{4,9}/[-._;()/:A-Z0-9]+$', re.IGNORECASE)
        if doi_pattern.match(url):
            doi = url.split('/')[-1]
            return f"\\href{{{url}}}{{DOI:{doi}}}"
        else:
            arxiv_pattern = re.compile(r'https?://arxiv\.org/abs/(\d+\.\d+)', re.IGNORECASE)
            m = arxiv_pattern.match(url)
            if m:
                aid = m.group(1)
                return f"\\href{{{url}}}{{arXiv:{aid}}}"
            else:
                return f"Unsupported URL format: {url}"
    else:
        return ""

def make_table(results, columns, translator, translate, service_urls):
    table_lines = []
    table_lines.append("\\begin{longtable}{|" + "P{\\autolength}|" * len(columns) + "}")
    table_lines.append("\\hline")
    header = " & ".join([f"\\textbf{{{col.capitalize()}}}" for col in columns])
    table_lines.append(header + " \\\\")
    table_lines.append("\\hline")
    for r in results:
        row = " & ".join([get_value(col, r, translator, translate, service_urls) for col in columns])
        table_lines.append(row + " \\\\ \\hline")
    table_lines.append("\\end{longtable}")
    return table_lines

def compile(file, mode, engine):
    base_name = file.rsplit('.', 1)[0]
    try:
        if mode == "auto":
            if engine in ["pdflatex", "xelatex", "lualatex"]:
                subprocess.run(f"{engine} {file}", shell=True, check=True)
            elif engine in ["uplatex", "platex", "latex"]:
                subprocess.run(f"{engine} {file}", shell=True, check=True)
                subprocess.run(f"dvipdfmx {base_name}.dvi", shell=True, check=True)
            else:
                raise ValueError(f"Unsupported engine: {engine}")
            cleanup_temp_files(base_name)
    except subprocess.CalledProcessError as e:
        print(f"Compilation failed: {e}")

def cleanup_temp_files(base_name):
    extensions = [
        "aux", "log", "dvi", "toc", "out", "nav", "snm", "ps",
        "bbl", "blg", "lof", "lot", "fdb_latexmk", "fls", "synctex.gz"
    ]
    for ext in extensions:
        file = f"{base_name}.{ext}"
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"Deleted: {file}")
            except PermissionError:
                print(f"Failed to delete: {file} (Permission denied)")
            except OSError as e:
                print(f"Failed to delete: {file} ({e})")

def main():
    args = parse_args()
    
    if args.translate:
        from googletrans import Translator
        
        def translator(text, dest, service_urls):
            if service_urls != None:
                tl = Translator(service_urls)
            else:
                tl = Translator()
            rst = tl.translate(text, dest=dest)
            return rst.text
    else:
        def translator(text, dest, service_urls):
            return text
        
    columns = [col.strip().lower() for col in args.columns.split(",")]
    for col in columns:
        if col not in ALLOWED_COLUMNS:
            raise ValueError(f"Invalid column '{col}'. Allowed columns are: {', '.join(ALLOWED_COLUMNS)}")

    sort_criterion = {
        "relevance": arxiv.SortCriterion.Relevance,
        "submittedDate": arxiv.SortCriterion.SubmittedDate,
        "lastUpdatedDate": arxiv.SortCriterion.LastUpdatedDate,
    }[args.sort_by]

    client = arxiv.Client()
    search = arxiv.Search(
        query=args.query,
        max_results=args.max_results,
        sort_by=sort_criterion
    )
    results = client.results(search)

    lines = []
    preamble(lines, args, columns)
    lines.append("\\begin{document}")
    lines.extend(make_table(results, columns, translator, args.translate, args.service_urls))
    lines.append("\\end{document}")

    output = f"{args.prefix}.tex"
    with open(output, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))

    compile(output, args.mode, args.engine)

if __name__ == "__main__":
    main()