from subprocess import run, PIPE, STDOUT, CalledProcessError
from pathlib import Path

from foliant.utils import spinner
from foliant.backends.base import BaseBackend
from foliant.preprocessors import flatten


class Backend(BaseBackend):
    _flat_src_file_name = '__all__.md'

    targets = ('pdf', 'docx', 'tex')

    required_preprocessors_before = {
        'flatten': {
            'flat_src_file_name': _flat_src_file_name
        }
    },

    def _get_vars_string(self) -> str:
        result = []

        for var_name, var_value in self._pandoc_config.get('vars', {}).items():
            if var_value is False:
                continue
            elif var_value is True:
                result.append(f'--variable {var_name}')
            else:
                result.append(f'--variable {var_name}="{var_value}"')

        return ' '.join(result)

    def _get_filters_string(self) -> str:
        result = []

        filters = self._pandoc_config.get('filters', ())

        for filter_ in filters:
            result.append(f'--filter {filter_}')

        return ' '.join(result)

    def _get_params_string(self) -> str:
        result = []

        for param_name, param_value in self._pandoc_config.get('params', {}).items():
            if param_value is False:
                continue
            elif param_value is True:
                result.append(f'--{param_name.replace("_", "-")}')
            else:
                result.append(f'--{param_name.replace("_", "-")}={param_value}')

        return ' '.join(result)

    def _get_from_string(self) -> str:
        markdown_flavor = self._pandoc_config.get('markdown_flavor', 'markdown')
        markdown_extensions = self._pandoc_config.get('markdown_extensions', ())

        return '+'.join((markdown_flavor, *markdown_extensions))

    def _get_pdf_command(self) -> str:
        components = [self._pandoc_config.get('pandoc_path', 'pandoc')]

        template = self._pandoc_config.get('template')
        if template:
            components.append(f'--template={template}')

        components.append(f'--output {self.get_slug()}.pdf')
        components.append(self._get_vars_string())
        components.append(self._get_filters_string())
        components.append(self._get_params_string())
        components.append(
            f'-f {self._get_from_string()} {self._flat_src_file_path}'
        )

        return ' '.join(components)

    def _get_docx_command(self) -> str:
        components = [self._pandoc_config.get('pandoc_path', 'pandoc')]

        reference_docx = self._pandoc_config.get('reference_docx')
        if reference_docx:
            components.append(f'--reference-doc={reference_docx}')

        components.append(f'--output {self.get_slug()}.docx')
        components.append(self._get_filters_string())
        components.append(self._get_params_string())
        components.append(
            f'-f {self._get_from_string()} {self._flat_src_file_path}'
        )

        return ' '.join(components)

    def _get_tex_command(self) -> str:
        components = [self._pandoc_config.get('pandoc_path', 'pandoc')]

        template = self._pandoc_config.get('template')
        if template:
            components.append(f'--template={template}')

        components.append(f'--output {self.get_slug()}.tex')
        components.append(self._get_vars_string())
        components.append(self._get_filters_string())
        components.append(self._get_params_string())
        components.append(
            f'-f {self._get_from_string()} {self._flat_src_file_path}'
        )

        return ' '.join(components)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._flat_src_file_path = self.working_dir / self._flat_src_file_name
        self._pandoc_config = self.config.get('backend_config', {}).get('pandoc', {})

    def make(self, target: str) -> str:
        with spinner(f'Making {target} with Pandoc', self.quiet):
            try:
                if target == 'pdf':
                    command = self._get_pdf_command()
                elif target == 'docx':
                    command = self._get_docx_command()
                elif target == 'tex':
                    command = self._get_tex_command()
                else:
                    raise ValueError(f'Pandoc cannot make {target}')

                run(command, shell=True, check=True, stdout=PIPE, stderr=STDOUT)
                return f'{self.get_slug()}.{target}'

            except CalledProcessError as exception:
                raise RuntimeError(f'Build failed: {exception.output.decode()}')

            except Exception as exception:
                raise type(exception)(f'Build failed: {exception}')
