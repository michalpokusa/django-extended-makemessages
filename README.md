
# django-extended-makemessages

<p float="left">
    <a href="https://pypi.org/project/django-extended-makemessages/">
        <img src="https://img.shields.io/pypi/v/django-extended-makemessages?color=0073b7"/>
    </a>
</p>

Extended version of Django's makemessages command that exposes selected GNU gettext tools options and adds new custom options, which further simplify message detection and translation files management.

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
