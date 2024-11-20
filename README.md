
# django-extended-makemessages

<p float="left">
    <a href="https://pypi.org/project/django-extended-makemessages/">
        <img src="https://img.shields.io/pypi/v/django-extended-makemessages?color=0073b7"/>
    </a>
</p>

Extended version of Django's makemessages command that exposes selected GNU gettext tools options and adds new custom options, which further simplify message detection and translation files management.

- [🎉 Features](#-features)
- [🔌 Instalation](#-instalation)
- [🚀 Overview](#-overview)
- [🧰 Usage](#-usage)

### 🎉 Features

All the options of `makemessages` command are available, plus:

- Sorting messages by `msgid` or by file location
- Disabling fuzzy translations
- Detecting message marked with `gettext` functions imported as aliases
- Keeping the header from constantly changing
- Extracting all string
- Removing flags from the output files

## 🔌 Instalation

> [!NOTE]
> This package is useful only during development. There is no need to install it in production environments.

1. Install using `pip`:

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

## 🚀 Overview

### Sorting messages by `msgid` or by file location

Django's `makemessages` command sorts messages based on location in the source code. This leads to situations where code refactoring can change in the order of messages in the `.po` file. As a result, the version control system shows a lot of changes that do not reflect the actual changes in the code and are confusing.

Below you can see, that despite only adding the `"Delivery"` message, the diff shows more changes.

<img src="https://raw.githubusercontent.com/michalpokusa/django-extended-makemessages/main/images/sorting-messages-by-msgid.png" width="100%"></img>

Using the `--sort-output` option will sort messages by `msgid` and as consequence, the diff will show only added/removed messages.

### Disabling fuzzy translations

By default, similar messages are marked as fuzzy and their translation is inferred from previously translated strings within the same .po file. This often leads to incorrect translations and requires additional manual review.

In the following example, `"Dessert"` (🍨🍰) is marked as fuzzy and its translation is inferred from the `"Desert"` (🐪🌵) message.

<img src="https://raw.githubusercontent.com/michalpokusa/django-extended-makemessages/main/images/disabling-fuzzy-translations-1.png" width="100%"></img>

You can use the `--no-fuzzy-matching` option to disable fuzzy matching. This way all messages will have to be translated manually.

<img src="https://raw.githubusercontent.com/michalpokusa/django-extended-makemessages/main/images/disabling-fuzzy-translations-2.png" width="100%"></img>


### Detecting messages marked with `gettext` functions imported as aliases

It is a common practice to <a href="https://docs.djangoproject.com/en/5.1/topics/i18n/translation/#standard-translation">import functions from `django.utils.translation` module as `_` alias</a>. This works because under the hood, `xgettext` command accepts it as one of the keywords for marking strings for translation.

That is not a problem, if you import only one function. However, if you need to import more than one function, you have to use its full name. This is because `xgettext` does not recognize aliases for functions other than `_`.

```python
from django.utils.translation import (
    gettext as _,
    gettext_lazy,
    pgettext,
    pgettext_lazy as pgtl,
)

_("This is fine.")  # ✅ Detected
gettext_lazy("On no, I have to use the full function name.")  # ✅ Detected
pgettext("opinion", "Yeah, that is not ideal.")  # ✅ Detected
pgtl("fact", "This message will not be detected.")  # ❌ Not detected
```

You can manually add aliases using the `--keyword` option with <a href="https://www.gnu.org/software/gettext/manual/html_node/xgettext-Invocation.html#Input-file-interpretation:~:text=%2D%2Dkeyword%5B%3Dkeywordspec%5D">this syntax</a>. However, a more convenient way is to use the `--detect-aliases` option, which will automatically recognize and add aliases for functions from the `django.utils.translation` module.

```python
from django.utils.translation import (
    gettext as gt,
    gettext_lazy as gtl,
    pgettext as pgt,
    pgettext_lazy as pgtl,
)

gt("This is fine.")  # ✅ Detected
gtl("And this also works.")  # ✅ Detected
pgt("opinion", "Using custom aliases is quite handy.")  # ✅ Detected
pgtl("fact", "This message will be detected.")  # ✅ Detected
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
