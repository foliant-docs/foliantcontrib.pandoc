# 1.1.0

-   Option to build separate chapters (sections) into separate files.

# 1.0.11

-   Do not re-raise an exception of the same type as raised, raise `RuntimeError` instead, it’s needed to avoid non-informative error messages.

# 1.0.10

-   Add backticks to the set of characters that should be escaped.

# 1.0.9

-   Escape double quotation marks (`"`) and dollar signs (`$`) which may be used in PDF, docx, and TeX generation commands as parts of filenames, variable values, etc. Enclose filenames that may be used in commands into double quotes.

# 1.0.8

-   Provide compatibility with Foliant 1.0.8.

# 1.0.7

-   Provide compatibility with Foliant 1.0.7.

# 1.0.6

-   Apply `flatten` after all preprocessors, not before them. This fixes incompatibility with foliantcontrib.includes 1.0.5.

# 1.0.5

-   Add `slug` config option.

# 1.0.4

-   Add logs.
-   Update for Foliant 1.0.4: Pass logger to spinner.
-   Require Foliant 1.0.4.

# 1.0.3

-   Change Pandoc command line parameter `--reference-docx` to `--reference-doc`.

# 1.0.2

-   Change default Markdown flavor from `markdown_strict` to `markdown`.

# 1.0.1

-   Add `tex` target.
