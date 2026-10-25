"""Rebuild the project page's images from the paper sources.

Run from the website root:
    python3 _tools/build_assets.py --paper ../../overleaf-paper

--paper  the revised paper's folder (main.tex, images/, qualitative-figures/). Nothing is written there.
Needs pdflatex, pdfcrop (TeX Live) and poppler's pdftoppm/pdftocairo.
Writes static/images/* and static/samples/*.png. Jekyll skips this _tools/ folder, so GitHub Pages does not publish it.
"""
from pathlib import Path
import argparse
import shutil
import subprocess
import tempfile

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / 'static' / 'images'
SAMPLES = ROOT / 'static' / 'samples'

# ICML 2023 layout: figures are typeset at these widths, so the LaTeX figures are rebuilt at the same size.
COLUMN, TEXT = '3.25in', '6.75in'

PREAMBLE = r'''\documentclass{article}
\usepackage[paperwidth=8in, paperheight=11in, margin=0.5in]{geometry}
\usepackage{times}
\usepackage{amsmath, amssymb, mathtools, calc, graphicx, extarrows, xcolor}
\usepackage[export]{adjustbox}
\usepackage{tikz}
\usetikzlibrary{positioning, arrows.meta, fit, calc}
\pagestyle{empty}
\setlength{\textwidth}{%(text)s}
\newlength{\itemwidth}
\newcommand{\ba}{\mathbf{a}}\newcommand{\bx}{\mathbf{x}}\newcommand{\bz}{\mathbf{z}}\newcommand{\bs}{\mathbf{s}}
\newcommand{\bh}{\mathbf{h}}\newcommand{\bb}{\mathbf{b}}\newcommand{\be}{\mathbf{e}}\newcommand{\bv}{\mathbf{v}}
\newcommand{\bmu}{{\boldsymbol{\mu}}}\newcommand{\bsigma}{{\boldsymbol{\sigma}}}
\graphicspath{{%(paper)s/}}
%% The paper's figure environments, without the float, caption and label.
\renewenvironment{figure}[1][]{\noindent\begin{minipage}{%(width)s}\centering}{\end{minipage}}
\renewenvironment{figure*}[1][]{\noindent\begin{minipage}{%(width)s}\centering}{\end{minipage}}
\renewcommand{\caption}[2][]{}
\renewcommand{\label}[1]{}
\begin{document}
'''

# name -> (source relative to the paper, typeset width, raster dpi or None for SVG)
# Figs. 3-5 of the paper: 64x64 samples arranged in LaTeX tables (PNG at about twice their on-page width).
LATEX_FIGURES = {
    'fig3_semantics': ('qualitative-figures/a_fixed_table.tex', COLUMN, 330),
    'fig4_smile': ('qualitative-figures/celeba_dis_dim0_table.tex', TEXT, 270),
    'fig5_interpolation': ('qualitative-figures/celeba_inter_table.tex', TEXT, 270),
}
# App. E architecture diagrams (TikZ): vector SVG.
ARCH_FIGURES = {
    'arch_unet': 'images/arch_unet.tex',
    'arch_blocks': 'images/arch_blocks.tex',
}

# Uncurated samples of App. J: the first 64 samples of the (0.1, 0.9) d_z=256 models, seed 0, guidance w=2.
SAMPLE_GRIDS = [f'{d}_{s}_w2' for d in ['fmnist', 'cifar10', 'celeba', 'ffhq'] for s in ['learned', 'prior']]


def run(*cmd, cwd=None):
    subprocess.run([str(c) for c in cmd], check=True, cwd=cwd, stdout=subprocess.DEVNULL)


def latex_pdf(body, width, paper, tmp, name):
    """Typeset `body` with the paper's figure macros at `width` and crop it to its ink."""
    tex = tmp / f'{name}.tex'
    tex.write_text(PREAMBLE % {'text': TEXT, 'paper': paper, 'width': width} + body + '\n\\end{document}\n')
    run('pdflatex', '-interaction=nonstopmode', '-halt-on-error', '-output-directory', tmp, tex, cwd=tmp)
    run('pdfcrop', '--margins', '4', tmp / f'{name}.pdf', tmp / f'{name}-crop.pdf', cwd=tmp)
    return tmp / f'{name}-crop.pdf'


def png(pdf, out, dpi):
    run('pdftoppm', '-png', '-cropbox', '-r', dpi, '-singlefile', pdf, out.with_suffix(''))
    Image.open(out).convert('RGB').save(out, optimize=True)


def build_figures(paper, tmp):
    IMAGES.mkdir(parents=True, exist_ok=True)
    # Fig. 1, the graphical abstract (photos): PNG.
    png(paper / 'images' / 'graphicalabstract.drawio_v2.pdf', IMAGES / 'fig1_overview.png', 360)
    # Fig. 2, the flow chart (PNG: it embeds photos), with the paper's trim (27 pt right, 21 pt bottom) that drops two stray drawio marks.
    pdf = latex_pdf(r'\includegraphics[trim=0 21 27 0, clip]{images/flowchart.drawio.pdf}', TEXT, paper, tmp, 'flowchart')
    png(pdf, IMAGES / 'fig2_flowchart.png', 300)
    for name, (src, width, dpi) in LATEX_FIGURES.items():
        png(latex_pdf(rf'\input{{{paper / src}}}', width, paper, tmp, name), IMAGES / f'{name}.png', dpi)
    for name, src in ARCH_FIGURES.items():
        pdf = latex_pdf(rf'\input{{{paper / src}}}', TEXT, paper, tmp, name)
        run('pdftocairo', '-svg', pdf, IMAGES / f'{name}.svg')


def build_icon(tmp):
    """Favicon: a bold z (the auxiliary latent) on the paper's link color."""
    body = (r'\definecolor{ourred}{RGB}{184,48,100}\begin{tikzpicture}'
            r'\useasboundingbox (0,0) rectangle (1,1);\fill[ourred, rounded corners=0.2cm] (0,0) rectangle (1,1);'
            r'\node[white, scale=3.2] at (0.5,0.53) {$\boldsymbol{z}$};\end{tikzpicture}')
    tex = tmp / 'icon.tex'
    tex.write_text('\\documentclass[border=0pt]{standalone}\\usepackage{amsmath,tikz}\\begin{document}' + body + '\\end{document}\n')
    run('pdflatex', '-interaction=nonstopmode', '-halt-on-error', '-output-directory', tmp, tex, cwd=tmp)
    run('pdftocairo', '-svg', tmp / 'icon.pdf', IMAGES / 'icon.svg')
    for size, name in [(32, 'favicon-32'), (180, 'apple-touch-icon')]:
        run('pdftoppm', '-png', '-scale-to', size, '-singlefile', tmp / 'icon.pdf', IMAGES / name)


def build_card():
    """The 1200x630 social-media card, from the rendered Fig. 1."""
    card = Image.new('RGB', (1200, 630), 'white')
    fig = Image.open(IMAGES / 'fig1_overview.png').convert('RGB')
    fig.thumbnail((1140, 590), Image.LANCZOS)
    card.paste(fig, ((1200 - fig.width) // 2, (630 - fig.height) // 2))
    card.save(IMAGES / 'og_image.png', optimize=True)


def build_samples(paper):
    """Copy the sample grids losslessly; the 32x32-pixel grids are doubled (nearest) so they stay sharp on screen."""
    SAMPLES.mkdir(parents=True, exist_ok=True)
    for name in SAMPLE_GRIDS:
        img = Image.open(paper / 'qualitative-figures' / 'samples' / f'{name}.png').convert('RGB')
        if img.width < 400:
            img = img.resize((img.width * 2, img.height * 2), Image.NEAREST)
        img.save(SAMPLES / f'{name}.png', optimize=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--paper', type=Path, required=True)
    args = ap.parse_args()
    paper = args.paper.resolve()
    with tempfile.TemporaryDirectory() as d:
        build_figures(paper, Path(d))
        build_icon(Path(d))
    build_card()
    build_samples(paper)
