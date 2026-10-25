# InfoDiffusion project page

Static page for *InfoDiffusion: Representation Learning Using Information Maximizing Diffusion Models* (ICML 2023; revised 2026) (Bulma, MathJax, no build step), served at https://yingheng-wang.com/infodiffusion-page/. Preview locally:

```bash
python3 -m http.server 8765   # then open http://127.0.0.1:8765/
```

- `index.html`: all text, tables and figures. Every number is from the revised paper (`overleaf-paper/main.tex`): Tables 1–5, Sec. 6.3 (FSQ latents), Sec. 6.5 (coefficients, samplers) and App. J (uncurated samples).
- GitHub Pages caches static files for 10 minutes: after changing the CSS or JS, bump the `?v=` suffix on their `<link>`/`<script>` tags in `index.html`.
- `static/js/index.js`: the uncurated-sample viewer (dataset tabs; the FIDs are the `w = 2` rows of Tables 2–3) and the BibTeX copy button.
- `static/images/`: paper figures (PNG for figures with photos, SVG for the TikZ architecture diagrams of App. E), the favicon and the 1200×630 social card (`og_image.png`, made from Fig. 1).
- `static/samples/<dataset>_<learned|prior>_w2.png`: the App. J grids, i.e. the first 64 samples (fixed seed, no selection) of the main configuration, (λ, ζ) = (0.1, 0.9), d_z = 256, first training seed, guidance w = 2. The paper's Fig. 10 shows the first 32 of the learned-prior grids. The 32×32-pixel grids (FashionMNIST, CIFAR10) are doubled with nearest-neighbour scaling so they stay sharp.
- `static/videos/infodiffusion_teaser.mp4`: the narrated teaser (~90 s; source, narration and renderer in `../infodiffusion-video/`), re-encoded for the web with the command below; its poster is `static/images/infodiffusion_teaser_poster.jpg`. It autoplays muted (the subtitles are burned in); "Play with sound" restarts it unmuted and turns off the loop. Bump the `?v=` on its `<source>` when replacing it. To re-encode a new render:

  ```bash
  FFMPEG=/path/to/ffmpeg   # e.g. the binary bundled with the Python package imageio-ffmpeg
  $FFMPEG -i ../infodiffusion-video/out/infodiffusion_teaser.mp4 -c:v libx264 -crf 25 -preset slow -pix_fmt yuv420p \
          -profile:v high -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
          -c:a copy -movflags +faststart static/videos/infodiffusion_teaser.mp4
  cp ../infodiffusion-video/out/infodiffusion_teaser_poster.jpg static/images/
  ```

- `_tools/build_assets.py`: regenerates `static/images/` and `static/samples/` from the paper folder (`--paper ../../overleaf-paper`). Fig. 1 is rendered from its PDF, Fig. 2 from the flow-chart PDF with the paper's trim (27 pt right, 21 pt bottom); Figs. 3–5 and the architecture diagrams are re-typeset from the paper's LaTeX at the ICML column/text width. Needs TeX Live (`pdflatex`, `pdfcrop`) and poppler. Jekyll does not publish `_tools/`.

The social-card URLs in `<head>` assume the page is served at `https://yingheng-wang.com/infodiffusion-page/`; update them if it moves.

The paper's qualitative figures (Figs. 1, 3–5) are the original ones; the tables and the uncurated samples come from the revised implementation (see `overleaf-paper/CHANGES.md`).

## Citation

```bibtex
@inproceedings{wang2023infodiffusion,
  title     = {{InfoDiffusion}: Representation Learning Using Information Maximizing Diffusion Models},
  author    = {Wang, Yingheng and Schiff, Yair and Gokaslan, Aaron and Pan, Weishen and Wang, Fei and De Sa, Christopher and Kuleshov, Volodymyr},
  booktitle = {Proceedings of the 40th International Conference on Machine Learning},
  series    = {Proceedings of Machine Learning Research},
  volume    = {202},
  pages     = {36336--36354},
  publisher = {PMLR},
  year      = {2023}
}
```

## Website license

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>. The page was built from the [Academic Project Page Template](https://github.com/eliahuhorwitz/Academic-project-page-template), which was adopted from the [Nerfies](https://nerfies.github.io) project page.
