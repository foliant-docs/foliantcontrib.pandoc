# Pandoc Backend for Foliant

[Pandoc](http://pandoc.org/) is a Swiss-army knife document converter. It converts almost any format to any other format: md to pdf, rst to html, adoc to docx, and so on and so on.

Pandoc backend for Foliant add `pdf`, `docx`, and `tex` targets.


## Installation

```shell
$ pip install foliantcontrib.pandoc
```

You also need to install Pandoc and TeXLive distribution for your platform.

## Usage

Build pdf:

```shell
$ foliant make pdf -p my-project
✔ Parsing config
✔ Applying preprocessor flatten
✔ Making pdf with Pandoc
─────────────────────
Result: My_Project-2017-12-04.pdf
```

Build docx:

```shell
$ foliant make docx -p my-project
✔ Parsing config
✔ Applying preprocessor flatten
✔ Making docx with Pandoc
─────────────────────
Result: My_Project-2017-12-04.docx
```

Build tex (mostly for pdf debugging):

```shell
$ foliant make tex -p my-project
✔ Parsing config
✔ Applying preprocessor flatten
✔ Making docx with Pandoc
─────────────────────
Result: My_Project-2017-12-04.tex
```


## Config

You don't have to put anything in the config to use Pandoc backend. If it's installed, Foliant will detect it.

You can however customize the backend with options in `backend_config.pandoc` section:

```yaml
backend_config:
  pandoc:
    pandoc_path: pandoc
    template: !path template.tex
    vars:
      ...
    reference_docx: !path reference.docx
    params:
      ...
    filters:
      ...
    markdown_flavor: markdown
    markdown_extensions:
      ...
    slug: My_Awesome_Custom_Slug
```

`pandoc_path`
:   is the path to `pandoc` executable. By default, it's assumed to be in the `PATH`.

`template`
:   is the path to the TeX template to use when building pdf and tex (see [“Templates”](http://pandoc.org/MANUAL.html#templates) in the Pandoc documentation).

    > **Tip**
    >
    > Use `!path` tag to ensure the value is converted into a valid path relative to the project directory.

`vars`
:   is a mapping of template variables and their values.

`reference_docx`
:   is the path to the reference document to used when building docx (see [“Templates”](http://pandoc.org/MANUAL.html#templates) in the Pandoc documentation).

    > **Tip**
    >
    > Use `!path` tag to ensure the value is converted into a valid path relative to the project directory.

`params`
:   are passed to the `pandoc` command. Params should be defined by their long names, with dashes replaced with underscores (e.g. `--pdf-engine` is defined as `pdf_engine`).

`filters`
:   is a list of Pandoc filters to be applied during build.

`markdown_flavor`
:   is the Markdown flavor assumed in the source. Default is `markdown`, [Pandoc's extended Markdown](http://pandoc.org/MANUAL.html#pandocs-markdown). See [“Markdown Variants”](http://pandoc.org/MANUAL.html#markdown-variants) in the Pandoc documentation.

`markdown_extensions`
:   is a list of Markdown extensions applied to the Markdown source. See [Pandoc’s Markdown](http://pandoc.org/MANUAL.html#pandocs-markdown) in the Pandoc documentation.

`slug`
:    is the result file name without suffix (e.g. `.pdf`). Overrides top-level config option `slug`.

Example config:

```yaml
backend_config:
  pandoc:
    template: !path templates/basic.tex
    vars:
      toc: true
      title: This Is a Title
      second_title: This Is a Subtitle
      logo: !path templates/logo.png
      year: 2017
    params:
      pdf_engine: xelatex
      listings: true
      number_sections: true
    markdown_extensions:
      - simple_tables
      - fenced_code_blocks
      - strikeout
```


## Troubleshooting

### Could not convert image ...: check that rsvg2pdf is in path

In order to use svg images in pdf, you need to have `rsvg-convert` executable in `PATH`.

On macOS, `brew install librsvg` does the trick. On Ubuntu, `apt install librsvg2-bin`. On Windows, [download `rsvg-convert.7z`](http://opensourcepack.blogspot.ru/2012/06/rsvg-convert-svg-image-conversion-tool.html) (without fontconfig support), unpack `rsvg-convert.exe`, and put it anywhere in `PATH`. For example, you can put it in the same directory where you run `foliant make`.

### LaTeX listings package does not work correctly with non-ASCII characters, e.g. Cyrillic letters

If you use non-ASCII characters inside backticks in your document, you can see an error like this:

```bash
Error producing PDF.
! Undefined control sequence.
\lst@arg ->git clone [SSH-к
                           люч]
l.627 ...through{\lstinline!git clone [SSH-ключ]!}
```

To fix it, set `listings` parameter to `false`:

```yaml
backend_config:
  pandoc:
    ...
    params:
      pdf_engine: xelatex
      listings: false
      number_sections: true
    ...
```
