import xml.etree.ElementTree as ET
from os.path import exists
from Types.Command import Command
from Types.Enum import Enum
import requests
import config


def download_spec():
    if not exists('../gl.xml'):
        spec = requests.get('https://www.khronos.org/registry/OpenGL/xml/gl.xml')
        open('../gl.xml', 'wb').write(spec.content)


class SpecReader:
    def __init__(self):
        download_spec()
        self.root = ET.parse("../gl.xml").getroot()
        self.required_enums: list[str] = []
        self.enums: list[Enum] = []
        self.commands: list[Command] = []

    def get_versions(self, api) -> list[str]:
        available_versions = set()
        for feature in self.root.findall(f"./feature[@api='{api}']"):
            available_versions.add(feature.attrib['number'])
        available_versions = list(available_versions)
        available_versions.sort()
        return available_versions

    def get_apis(self) -> list[str]:  # TODO this does not work properly
        available_apis = set()
        for feature in self.root.findall(f"./feature"):
            available_apis.add(feature.attrib['api'])
        available_apis = list(available_apis)
        available_apis.sort()
        return available_apis

    def parse(self):
        for feature in self.root.findall(f"./feature[@api='{config.API}']"):
            if feature.attrib['number'] > config.TARGET_VERSION:
                continue

            for requirement in feature.findall('./require/enum'):
                self.required_enums.append(requirement.attrib['name'])

        for required_enum in self.required_enums:
            enum_node = self.root.find(f"./enums/enum[@name='{required_enum}']")
            enum = Enum(enum_node.attrib['name'], enum_node.attrib['value'])
            if 'group' in enum_node.attrib.keys():
                enum.group = enum_node.attrib['group']
            self.enums.append(enum)

        # Read commands
        for command_node in self.root.findall("./commands/command"):
            name_node = command_node.find('./proto/name')
            # Check if we require this command for target version
            # FIXME something is not right here
            if self.root.find(f"./feature[@api='{config.API}']/require/command[@name='{name_node.text}']") is None:
                continue
            type_node = command_node.find('./proto/ptype')
            return_type = type_node.text if type_node is not None else 'void'
            params = []
            for param_node in command_node.findall('./param'):
                params.append(ET.tostring(param_node, method='text', encoding='unicode').strip())
            self.commands.append(Command(name_node.text, return_type, params))
