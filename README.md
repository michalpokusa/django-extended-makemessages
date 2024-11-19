
# django-extended-makemessages

<p float="left">
    <a href="https://pypi.org/project/django-extended-makemessages/">
        <img src="https://img.shields.io/pypi/v/django-extended-makemessages?color=0073b7"/>
    </a>
</p>

Extended version of Django's makemessages command that exposes selected GNU gettext tools options and adds new custom options, which further simplify message detection and translation files management.

- [🎉 Features](#-features)
- [🔌 Instalation](#-instalation)
- [🧰 Usage](#-usage)

### 🎉 Features

- Disabling fuzzy translations
- Sorting messages by `msgid` or by file location
- Detecting message marked witg `gettext` functions imported as aliases
- Extracting all string
- Removing flags from the output files

## 🔌 Instalation

> [!NOTE]
> This package is useful only during development. There is no need to install it in production environments.

1. Install using ``pip``:

    ```bash
    $ pip3 install django-extended-makemessages
    ```


2. Add `'django_extended_makemessages'` to your `INSTALLED_APPS` setting.
    ```python
    INSTALLED_APPS = [
        ...
        'django_extended_makemessages',
    ]
    ```

## 🧰 Usage

```
usage:  extendedmakemessages [-h] [--locale LOCALE] [--exclude EXCLUDE] [--domain DOMAIN] [--all] [--extension EXTENSIONS]
                             [--symlinks] [--ignore PATTERN] [--no-default-ignore] [--no-wrap] [--no-location]
                             [--add-location [{full,file,never}]] [--no-obsolete] [--keep-pot] [--no-fuzzy-matching]
                             [--extract-all] [--keyword [KEYWORD]] [--force-po] [--indent] [--width WIDTH]
                             [--sort-output | --sort-by-file] [--detect-aliases] [--keep-header] [--no-flags]
                             [--no-flag {fuzzy,python-format,python-brace-format,no-python-format,no-python-brace-format}]
                             [--no-previous] [--version] [-v {0,1,2,3}] [--settings SETTINGS] [--pythonpath PYTHONPATH]
                             [--traceback] [--no-color] [--force-color]

Runs over the entire source tree of the current directory and pulls out all strings marked for translation. It creates (or updates)
a message file in the conf/locale (in the django tree) or locale (for projects and applications) directory.

You must run this command with one of either the --locale, --exclude, or --all options.

In addition to the options available in Django's makemessages command, this command exposes selected
msgmerge/msguniq/msgattrib/xgettext options that make sense for usage in a Django project.

On top of that, this command also includes some custom options, which further simplify managing translations in a Djangoprojects,
but are not part of GNU gettext tools.

options:
  -h, --help            show this help message and exit
  --locale LOCALE, -l LOCALE
                        Creates or updates the message files for the given locale(s) (e.g. pt_BR). Can be used multiple
                        times.
  --exclude EXCLUDE, -x EXCLUDE
                        Locales to exclude. Default is none. Can be used multiple times.
  --domain DOMAIN, -d DOMAIN
                        The domain of the message files (default: "django").
  --all, -a             Updates the message files for all existing locales.
  --extension EXTENSIONS, -e EXTENSIONS
                        The file extension(s) to examine (default: "html,txt,py", or "js" if the domain is "djangojs").
                        Separate multiple extensions with commas, or use -e multiple times.
  --symlinks, -s        Follows symlinks to directories when examining source code and templates for translation strings.
  --ignore PATTERN, -i PATTERN
                        Ignore files or directories matching this glob-style pattern. Use multiple times to ignore more.
  --no-default-ignore   Don't ignore the common glob-style patterns 'CVS', '.*', '*~' and '*.pyc'.
  --no-wrap             Don't break long message lines into several lines.
  --no-location         Don't write '#: filename:line' lines.
  --add-location [{full,file,never}]
                        Controls '#: filename:line' lines. If the option is 'full' (the default if not given), the lines
                        include both file name and line number. If it's 'file', the line number is omitted. If it's
                        'never', the lines are suppressed (same as --no-location). --add-location requires gettext 0.19 or
                        newer.
  --no-obsolete         Remove obsolete message strings.
  --keep-pot            Keep .pot file after making messages. Useful when debugging.
  --no-fuzzy-matching   Do not use fuzzy matching when an exact match is not found. This may speed up the operation
                        considerably.
  --extract-all         Extract all strings.
  --keyword [KEYWORD]   Specify keywordspec as an additional keyword to be looked for. Without a keywordspec, the option
                        means to not use default keywords.
  --force-po            Always write an output file even if no message is defined.
  --indent              Write the .po file using indented style.
  --width WIDTH         Set the output page width. Long strings in the output files will be split across multiple lines in
                        order to ensure that each line's width (= number of screen columns) is less or equal to the given
                        number.
  --sort-output         Generate sorted output.
  --sort-by-file        Sort output by file location.
  --detect-aliases      Detect gettext functions aliases in the project and add them as keywords to xgettext command.
  --keep-header         Keep the header of the .po file exactly the same as it was before the command was run. Do nothing
                        if the .po file does not exist.
  --no-flags            Don't write '#, flags' lines.
  --no-flag {fuzzy,python-format,python-brace-format,no-python-format,no-python-brace-format}
                        Remove specific flag from the '#, flags' lines.
  --no-previous         Don't write '#| previous' lines.
  --version             Show program's version number and exit.
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output
  --settings SETTINGS   The Python path to a settings module, e.g. "myproject.settings.main". If this isn't provided, the
                        DJANGO_SETTINGS_MODULE environment variable will be used.
  --pythonpath PYTHONPATH
                        A directory to add to the Python path, e.g. "/home/djangoprojects/myproject".
  --traceback           Raise on CommandError exceptions.
  --no-color            Don't colorize the command output.
  --force-color         Force colorization of the command output.
```
