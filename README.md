# Pandoc Backend for Foliant

[Pandoc](http://pandoc.org/) is a Swiss-army knife document converter. It converts almost any format to any other format: md to pdf, rst to html, adoc to docx, and so on and so on.

Pandoc backend for Foliant add `pdf` and `docx` targets.


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


## Config

You don't have to put anything in the config to use Pandoc backend. If it's installed, Foliant will detect it.

You can however customize the backend with options in `backend_config.pandoc` section:

```yaml
backend_config:
  pandoc:
    binary_path: pandoc
    template: !path template.tex
    vars:
      ...
    reference_docx: !path reference.docx
    params:
      ...
    filters:
      ...
    markdown_flavor: markdown_strict
    markdown_extensions:
      ...
```

`binary_path`
:   is the path to `pandoc` executable. By default, it's assumed to be in the `PATH`.

`template`
:   is the path to the TeX template to use when building pdf (see [“Templates”](http://pandoc.org/MANUAL.html#templates) in the Pandoc documentation).

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
:   is the Markdown flavor assumed in the source. Default is `markdown_strict`, which is the original Markdown by John Gruber. See [“Markdown Variants”](http://pandoc.org/MANUAL.html#markdown-variants) in the Pandoc documentation.

`markdown_extensions`
:   is a list of Markdown extensions applied to the Markdown source. See [Pandoc’s Markdown](http://pandoc.org/MANUAL.html#pandocs-markdown) in the Pandoc documentation.

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