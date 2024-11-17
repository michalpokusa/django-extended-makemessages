python3 -c "
from pathlib import Path

pyproject_file = Path('pyproject.toml')
pyproject_template = pyproject_file.read_text()
pyproject_file.write_text(
    pyproject_template.replace('%PACKAGE_VERSION%', '$PACKAGE_VERSION')
)

package_init_file = Path('django_extended_makemessages/__init__.py')
package_init_template = package_init_file.read_text()
package_init_file.write_text(
    package_init_template.replace('%PACKAGE_VERSION%', '$PACKAGE_VERSION')
)
"

python3 -m build
