# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2025-01-13

### Changed

- `--no-untranslated` option outputs which msgstr is untranslated and its location in the .po file

## [1.3.0] - 2024-12-31

### Added

- `--add-comments` option for copying comments from the source code to the .po file

## [1.2.0] - 2024-12-23

### Added

- `--no-untranslated` option that checks for untranslated strings in the .po files

## [1.1.3] - 2024-12-13

### Fixed

- `--dry-run` option now restores the .po file to its original state when the `makemessages` command fails

## [1.1.1] - 2024-12-05

### Fixed

- Updated regex for header detection to work with `--indent` option.

## [1.1.0] - 2024-11-27

### Added

- `--check` option that checks if .po files are up to date with source code
- `--dry-run` option that restores the .po file to its original state after running the command
- Section in README.md about `--check` option

## [1.0.0] - 2024-11-22

### Added

- `--no-fuzzy-matching` option that disables fuzzy matching
- `--extract-all` option that extracts all strings from the code
- `--keyword` option that allows to specify custom xgettext command keywords
- `--force-po` option that forces writing to the .po file even if it is empty
- `--indent` option that writes the .po file using indented style
- `--width` option that sets the output page width
- `--sort-output` option that sorts output by msgid
- `--sort-by-file` option that sorts output by message location in the source code
- `--detect-aliases` option that detects messages marked by functions from `django.utils.translation` module imported as aliases
- `--keep-header` option that prevents the .po file header from being changed by makemessages
- `--no-flags` option that removes all `#, ...` lines from the output
- `--no-flag` option that removes specific flag from `#, ...` lines from the output
- `--no-previous` option that removes all `'#| ...'` lines from the output
- README.md file with overview, installation and usage instructions

[1.4.0]: https://github.com/michalpokusa/django-extended-makemessages/compare/1.3.0...1.4.0
[1.3.0]: https://github.com/michalpokusa/django-extended-makemessages/compare/1.2.0...1.3.0
[1.2.0]: https://github.com/michalpokusa/django-extended-makemessages/compare/1.1.3...1.2.0
[1.1.3]: https://github.com/michalpokusa/django-extended-makemessages/compare/1.1.1...1.1.3
[1.1.1]: https://github.com/michalpokusa/django-extended-makemessages/compare/1.1.0...1.1.1
[1.1.0]: https://github.com/michalpokusa/django-extended-makemessages/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/michalpokusa/django-extended-makemessages/tree/1.0.0
