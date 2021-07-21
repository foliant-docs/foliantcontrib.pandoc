import os
import shutil

from contextlib import contextmanager
from datetime import date
from pathlib import Path
from pathlib import PosixPath
from subprocess import CalledProcessError
from subprocess import PIPE
from subprocess import STDOUT
from subprocess import run
from typing import Union

from foliant.backends.base import BaseBackend
from foliant.meta.generate import load_meta
from foliant.utils import spinner


@contextmanager
def chcwd(newcwd: Union[str, Path], *args, **kwargs):
    '''
    Temporary change working directory to `newcwd`
    '''

    init_cwd = os.getcwd()
    try:
        os.chdir(newcwd)
        yield
    finally:
        os.chdir(init_cwd)


class Backend(BaseBackend):
    _flat_src_file_name = '__all__.md'

    targets = ('pdf', 'docx', 'tex')

    defaults = {
        'build_whole_project': True
    }

    required_preprocessors_after = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._flat_src_file_path = self.working_dir / self._flat_src_file_name
        self._base_pandoc_config = self._pandoc_config = {
            **self.defaults,
            **self.config.get(
                'backend_config',
                {}
            ).get('pandoc', {})
        }
        if self._pandoc_config['build_whole_project']:
            self.required_preprocessors_after = {
                'flatten': {
                    'flat_src_file_name': self._flat_src_file_name,
                    'keep_sources': True
                }
            },

        self.cache_dir = Path('.pandoccache')
        shutil.rmtree(self.cache_dir, ignore_errors=True)
        self.cache_dir.mkdir()

        self.logger = self.logger.getChild('pandoc')

        self.logger.debug(f'Backend inited: {self.__dict__}')

    def get_slug_overall(self) -> str:
        if 'slug' in self._pandoc_config:
            slug = self._pandoc_config['slug']
        elif 'slug' in self.config:
            slug = self.config['slug']
        else:
            components = []

            components.append(self.config['title'].replace(' ', '_'))

            version = self.config.get('version')
            if version:
                components.append(str(version))

            components.append(str(date.today()))

            slug = '-'.join(components)

        slug_for_commands = self._escape_control_characters(slug)
        return slug, slug_for_commands

    def get_slug_for_section(self, section) -> str:
        if 'slug' in self._pandoc_config:
            slug = self._pandoc_config['slug']
        else:
            components = []

            components.append(section.title.replace(' ', '_'))

            version = section.data.get('version')\
                or section.data.get('vars', {}).get('version')\
                or self.config.get('version')
            if version:
                components.append(str(version))

            components.append(str(date.today()))

            slug = '-'.join(components)

        slug_for_commands = self._escape_control_characters(slug)
        return slug, slug_for_commands

    def _escape_control_characters(self, source_string: str) -> str:
        escaped_string = source_string.replace('"', "\\\"").replace('$', "\\$").replace('`', "\\`")

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

    def _get_metadata_string(self) -> str:
        result = []

        for meta_name, meta_value in self._pandoc_config.get('meta', {}).items():
            if meta_value is False:
                continue
            elif meta_value is True:
                result.append(f'--metadata {meta_name}')
            else:
                result.append(f'--metadata {meta_name}="{self._escape_control_characters(str(meta_value))}"')

        vars_string = ' '.join(result)

        self.logger.debug(f'Metadata string: {vars_string}')

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

    def _get_pdf_command(
        self,
        source_path: str or PosixPath,
        slug: str
    ) -> str:
        components = [self._pandoc_config.get('pandoc_path', 'pandoc')]

        template = self._pandoc_config.get('template')

        if template:
            components.append(f'--template="{self._escape_control_characters(str(template))}"')

        components.append(f'--output "{slug}.pdf"')
        components.append(self._get_vars_string())
        components.append(self._get_metadata_string())
        components.append(self._get_filters_string())
        components.append(self._get_params_string())
        components.append(
            f'-f {self._get_from_string()} {source_path}'
        )

        command = ' '.join(components)

        self.logger.debug(f'PDF generation command: {command}')

        return command

    def _get_docx_command(
        self,
        source_path: str or PosixPath,
        slug: str
    ) -> str:
        components = [self._pandoc_config.get('pandoc_path', 'pandoc')]

        reference_docx = self._pandoc_config.get('reference_docx')

        if reference_docx:
            components.append(f'--reference-doc="{self._escape_control_characters(str(reference_docx))}"')

        components.append(f'--output "{slug}.docx"')
        components.append(self._get_metadata_string())
        components.append(self._get_filters_string())
        components.append(self._get_params_string())
        components.append(
            f'-f {self._get_from_string()} {source_path}'
        )

        command = ' '.join(components)

        self.logger.debug(f'Docx generation command: {command}')

        return command

    def _get_tex_command(
        self,
        source_path: str or PosixPath,
        slug: str
    ) -> str:
        components = [self._pandoc_config.get('pandoc_path', 'pandoc')]

        template = self._pandoc_config.get('template')

        if template:
            components.append(f'--template="{self._escape_control_characters(str(template))}"')

        components.append(f'--output "{slug}.tex"')
        components.append(self._get_vars_string())
        components.append(self._get_metadata_string())
        components.append(self._get_filters_string())
        components.append(self._get_params_string())
        components.append(
            f'-f {self._get_from_string()} {source_path}'
        )

        command = ' '.join(components)

        self.logger.debug(f'TeX generation command: {command}')

        return command

    def _build_flat(self, target: str) -> str:
        slug, slug_for_commands = self.get_slug_overall()
        try:
            if target == 'pdf':
                command = self._get_pdf_command(
                    self._flat_src_file_path,
                    slug_for_commands
                )
            elif target == 'docx':
                command = self._get_docx_command(
                    self._flat_src_file_path,
                    slug_for_commands
                )
            elif target == 'tex':
                command = self._get_tex_command(
                    self._flat_src_file_path,
                    slug_for_commands
                )
            else:
                raise ValueError(f'Pandoc cannot make {target}')

            self.logger.debug('Running the command.')

            run(command, shell=True, check=True, stdout=PIPE, stderr=STDOUT)

            return f'{slug}.{target}'

        except CalledProcessError as exception:
            raise RuntimeError(f'Build failed: {exception.output.decode()}')

        except Exception as exception:
            raise RuntimeError(f'Build failed: {exception}')

    def _serialize_section(self, section, slug: str) -> Path:
        """
        Save section content into a "_md" file (to avoid name clashes) into the
        same dir as the section's chapter (for paths to images to work).
        """
        filename = Path(section.chapter.filename).parent / f'{slug}._md'
        counter = 1
        while filename.exists():
            counter += 1
            filename = filename.parent / f'{slug}{counter}.md'
        self.logger.debug(f'Serializing section {section} into {filename}')
        with open(filename, 'w') as f:
            f.write(section.get_source())
        return filename

    def _build_separate(self, target: str) -> str:
        result = []
        for section in self.meta.iter_sections():
            local_pandoc_config = section.data.get('pandoc', {})
            if local_pandoc_config:
                self.logger.debug(f'Found section with pandoc meta: {section.id}')
                if not isinstance(local_pandoc_config, dict):
                    local_pandoc_config = {}
                self._pandoc_config = {**self._base_pandoc_config, **local_pandoc_config}
                slug, slug_for_commands = self.get_slug_for_section(section)
                slug_for_commands = os.path.join(os.getcwd(), slug_for_commands)
                self.logger.debug(f'Generated absolute slug: {slug_for_commands}')

                if section.is_main():
                    source_dir, filename = os.path.split(
                        section.chapter.filename
                    )
                else:
                    source_dir, filename = os.path.split(
                        self._serialize_section(section, slug)
                    )
                self.logger.debug(f'Section to build: {source_dir=}, {filename=}')
                try:
                    if target == 'pdf':
                        command = self._get_pdf_command(
                            filename,
                            slug_for_commands
                        )
                    elif target == 'docx':
                        command = self._get_docx_command(
                            filename,
                            slug_for_commands
                        )
                    elif target == 'tex':
                        command = self._get_tex_command(
                            filename,
                            slug_for_commands
                        )
                    else:
                        raise ValueError(f'Pandoc cannot make {target}')

                    self.logger.debug('Running the command.')
                    with chcwd(source_dir):
                        run(command, shell=True, check=True, stdout=PIPE, stderr=STDOUT)

                    result.append(f'{slug}.{target}')

                except CalledProcessError as exception:
                    raise RuntimeError(f'Build failed: {exception.output.decode()}')

                except Exception as exception:
                    raise RuntimeError(f'Build failed: {exception}')
            else:
                continue
        return result

    def make(self, target: str) -> str:
        self.meta = load_meta(self.config.get('chapters', []), self.working_dir)
        with spinner(f'Making {target} with Pandoc', self.logger, self.quiet, self.debug):
            result = []
            if self._pandoc_config['build_whole_project']:
                result.append(self._build_flat(target))
            result.extend(self._build_separate(target))
            return '\n' + '\n'.join(result)
