import xml.etree.ElementTree as ET
from os.path import exists
from Command import Command
import requests
import config


def download_spec():
    if not exists('gl.xml'):
        spec = requests.get('https://www.khronos.org/registry/OpenGL/xml/gl.xml')
        open('gl.xml', 'wb').write(spec.content)


class SpecReader:
    def __init__(self, file):
        download_spec()
        self.root = ET.parse("gl.xml").getroot()
        self.required_enums = []
        self.commands = []

    def get_versions(self, api):
        pass

    def parse(self):
        for feature in self.root.findall(f"./feature[@api='{config.API}']"):
            if float(feature.attrib['number']) > config.TARGET_VERSION:
                continue

            # Enums
            for requirement in feature.findall('./require/enum'):
                self.required_enums.append(requirement.attrib['name'])

        # Read commands
        for command_node in self.root.findall("./commands/command"):
            name_node = command_node.find('./proto/name')
            # Check if we require this command for target version
            if self.root.find(f"./feature[@api='{config.API}']/require/command[@name='{name_node.text}']") is None:
                continue
            type_node = command_node.find('./proto/ptype')
            return_type = type_node.text if type_node is not None else 'void'
            params = []
            for param_node in command_node.findall('./param'):
                params.append(ET.tostring(param_node, method='text', encoding='unicode').strip())
            self.commands.append(Command(name_node.text, return_type, params))
