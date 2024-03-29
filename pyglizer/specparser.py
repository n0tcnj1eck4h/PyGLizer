from io import IOBase
from xml.etree.ElementTree import Element, parse, tostring
from .command import Command
from .glenum import GLEnum
from .specinfo import SpecInfo


class SpecParser:
    def __init__(self, source: IOBase):
        self.root: Element = parse(source).getroot()

    def get_versions(self, api: str) -> list[str]:
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

    def parse(self, api: str, version: str):
        required_enums: list[str] = []
        required_commands: list[str] = []
        enums: list[GLEnum] = []
        commands: list[Command] = []
        types: list[str] = []

        for feature in self.root.findall(f"./feature[@api='{api}']"):
            if feature.attrib['number'] > version:
                continue

            for requirement in feature.findall('./require/enum'):
                required_enums.append(requirement.attrib['name'])

            for requirement in feature.findall('./require/command'):
                required_commands.append(requirement.attrib['name'])

        for required_enum in required_enums:
            enum_node = self.root.find(f"./enums/enum[@name='{required_enum}']")
            enum = GLEnum(enum_node.attrib['name'], enum_node.attrib['value'])
            if 'group' in enum_node.attrib.keys():
                enum.group = enum_node.attrib['group']
            enums.append(enum)

        for command_node in self.root.findall("./commands/command"):
            name_node = command_node.find('./proto/name')
            command_name = name_node.text
            if command_name not in required_commands:
                continue

            type_node = command_node.find('./proto/ptype')
            return_type = type_node.text if type_node is not None else 'void'

            params = []
            for param_node in command_node.findall('./param'):
                params.append(tostring(param_node, method='text', encoding='unicode').strip())

            commands.append(Command(command_name, return_type, params))

        # TODO apientry
        for type in self.root.findall("./types/type"):
            types.append(tostring(type, method='text', encoding='unicode').strip())  # this is still stupid

        return SpecInfo(api, version, enums, commands, types)
