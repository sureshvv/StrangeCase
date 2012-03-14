import os
import jinja2
import jinja2.ext
from scss import Scss

from strange_case.registry import Registry
from strange_case.nodes import FileNode


scss_compiler = Scss().compile


class ScssExtension(jinja2.ext.Extension):
    tags = set(['scss'])

    def __init__(self, environment):
        super(ScssExtension, self).__init__(environment)

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        body = parser.parse_statements(
            ['name:endscss'],
            drop_needle=True
        )
        return jinja2.nodes.CallBlock(
            self.call_method('_scss_support'),
            [],
            [],
            body
        ).set_lineno(lineno)

    def _scss_support(self, caller):
        return scss_compiler(caller()).strip()


class ScssNode(FileNode):
    """
    Converts a .scss file into css
    """
    def generate_file(self, site, source_path, target_path):
        scss_content = open(source_path, 'r').read()
        css_content = scss_compiler(scss_content)
        with open(target_path) as f:
            f.write(css_content)
        self.files_written.append(target_path)


def scss_processor(config, source_path, target_path):
    if config['target_name'][-4:] == 'scss':
        config['target_name'][-4:] = 'css'

    scss_node = ScssNode(config, source_path, target_path)
    return (scss_node,)

Registry.register('scss', scss_processor)
Registry.associate('scss', ['*.scss'])
