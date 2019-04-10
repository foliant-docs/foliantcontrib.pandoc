from subprocess import run, PIPE, STDOUT, CalledProcessError
from pathlib import Path

from foliant.utils import spinner
from foliant.backends.base import BaseBackend
from foliant.preprocessors import flatten


class Backend(BaseBackend):
    _flat_src_file_name = '__all__.md'

    targets = ('pdf', 'docx', 'tex')

    required_preprocessors_after = {
        'flatten': {
            'flat_src_file_name': _flat_src_file_name
        }
    },

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._flat_src_file_path = self.working_dir / self._flat_src_file_name
        self._pandoc_config = self.config.get('backend_config', {}).get('pandoc', {})
        self._slug = f'{self._pandoc_config.get("slug", self.get_slug())}'
        self._slug_for_commands = self._escape_control_characters(str(self._slug))

        self.logger = self.logger.getChild('pandoc')

        self.logger.debug(f'Backend inited: {self.__dict__}')

    def _escape_control_characters(self, source_string: str) -> str:
        escaped_string = source_string.replace('"', "\\\"").replace('$', "\\$")

        return escaped_string

    def _get_vars_string(self) -> str:
        result = []

        for var_name, var_value in self._pandoc_config.get('vars', {}).items():
            if var_value is False:
                continue
            elif var_value is True:
                result.append(f'--variable {var_name}')
            else:
                result.append(f'--variable {var_name}="{self._escape_control_characters(str(var_value))}"')

        vars_string = ' '.join(result)

        self.logger.debug(f'Vars string: {vars_string}')

        return vars_string

    def _get_filters_string(self) -> str:
        result = []

        filters = self._pandoc_config.get('filters', ())

        for filter_ in filters:
            result.append(f'--filter {filter_}')

        filters_string = ' '.join(result)

        self.logger.debug(f'Filters string: {filters_string}')

        return filters_string

    def _get_params_string(self) -> str:
        result = []

        for param_name, param_value in self._pandoc_config.get('params', {}).items():
            if param_value is False:
                continue
            elif param_value is True:
                result.append(f'--{param_name.replace("_", "-")}')
            else:
                result.append(f'--{param_name.replace("_", "-")}={param_value}')

        params_string = ' '.join(result)

        self.logger.debug(f'Params string: {params_string}')

        return params_string

    def _get_from_string(self) -> str:
        markdown_flavor = self._pandoc_config.get('markdown_flavor', 'markdown')
        markdown_extensions = self._pandoc_config.get('markdown_extensions', ())

        from_string = '+'.join((markdown_flavor, *markdown_extensions))

        self.logger.debug(f'From string: {from_string}')

        return from_string

    def _get_pdf_command(self) -> str:
        components = [self._pandoc_config.get('pandoc_path', 'pandoc')]

        template = self._pandoc_config.get('template')

        if template:
            components.append(f'--template="{self._escape_control_characters(str(template))}"')

        components.append(f'--output "{self._slug_for_commands}.pdf"')
        components.append(self._get_vars_string())
        components.append(self._get_filters_string())
        components.append(self._get_params_string())
        components.append(
            f'-f {self._get_from_string()} {self._flat_src_file_path}'
        )

        command = ' '.join(components)

        self.logger.debug(f'PDF generation command: {command}')

        return command

    def _get_docx_command(self) -> str:
        components = [self._pandoc_config.get('pandoc_path', 'pandoc')]

        reference_docx = self._pandoc_config.get('reference_docx')

        if reference_docx:
            components.append(f'--reference-doc="{self._escape_control_characters(str(reference_docx))}"')

        components.append(f'--output "{self._slug_for_commands}.docx"')
        components.append(self._get_filters_string())
        components.append(self._get_params_string())
        components.append(
            f'-f {self._get_from_string()} {self._flat_src_file_path}'
        )

        command = ' '.join(components)

        self.logger.debug(f'Docx generation command: {command}')

        return command

    def _get_tex_command(self) -> str:
        components = [self._pandoc_config.get('pandoc_path', 'pandoc')]

        template = self._pandoc_config.get('template')

        if template:
            components.append(f'--template="{self._escape_control_characters(str(template))}"')

        components.append(f'--output "{self._slug_for_commands}.tex"')
        components.append(self._get_vars_string())
        components.append(self._get_filters_string())
        components.append(self._get_params_string())
        components.append(
            f'-f {self._get_from_string()} {self._flat_src_file_path}'
        )

        command = ' '.join(components)

        self.logger.debug(f'TeX generation command: {command}')

        return command

    def make(self, target: str) -> str:
        with spinner(f'Making {target} with Pandoc', self.logger, self.quiet, self.debug):
            try:
                if target == 'pdf':
                    command = self._get_pdf_command()
                elif target == 'docx':
                    command = self._get_docx_command()
                elif target == 'tex':
                    command = self._get_tex_command()
                else:
                    raise ValueError(f'Pandoc cannot make {target}')

                self.logger.debug('Running the command.')

                run(command, shell=True, check=True, stdout=PIPE, stderr=STDOUT)

                return f'{self._slug}.{target}'

            except CalledProcessError as exception:
                raise RuntimeError(f'Build failed: {exception.output.decode()}')

            except Exception as exception:
                raise type(exception)(f'Build failed: {exception}')
