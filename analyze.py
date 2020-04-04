#!/usr/bin/env python3

import jstyleson
from tabulate import tabulate

os_list = ['windows', 'linux', 'macos']

# List of all commands and bindings across all OSs.
# Each element of this list is in this schema:
# {
#     'command': "COMMAND",
#     'when': "WHEN",
#     'windows': "KEY",
#     'linux': "KEY",
#     'macos': "KEY",
# }
entries = []

windows_vk_mapping = (
    # These must be sorted from longest to shortest to avoid 'oem_1' from matching 'oem_14', etc.
    ('oem_period', '.'),
    ('oem_comma', ','),
    ('oem_minus', '-'),
    ('oem_plus', '='),
    ('oem_1', ';'),
    ('oem_2', '/'),
    ('oem_3', '`'),
    ('oem_4', '['),
    ('oem_5', '\\'),
    ('oem_6', ']'),
    # See this page for more: https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes?redirectedfrom=MSDN
)

unmapped_vks = []


def replace_windows_vk(key):
    for mapping in windows_vk_mapping:
        key = key.replace(mapping[0], mapping[1])
    if 'oem_' in key:
        unmapped_vks.append(key)
    return key


# Load default keybindings
for os in os_list:
    for file in ('default-keybindings.json', 'keybindings.json'):
        try:
            path = f"{os}/{file}"
            print(f"Opening {path}")
            with open(path) as f:
                bindings = jstyleson.load(f)
        except FileNotFoundError:
            continue

        for binding in bindings:
            # Command to execute
            command = binding['command']
            delete_mode = command[0] == '-'
            if delete_mode:
                command = command[1:]

            # Conditions to command execution
            when = binding.get('when')

            # Key that must be pressed
            key = binding['key']
            if os == 'windows':
                key = replace_windows_vk(key)

            # Find a matching entry or create a new entry
            for entry in entries:
                if entry['command'] == command and entry['when'] == when:
                    break
            else:
                entry = {'command': command, 'when': when}
                entries.append(entry)

            if command == 'workbench.action.closeActiveEditor' and os == 'linux':
                print('Before', entry)

            # Update the entry
            if entry.get(os):
                entry['orig_' + os] = entry[os]
            if delete_mode:
                entry[os] = None
            else:
                entry[os] = key

            if command == 'workbench.action.closeActiveEditor' and os == 'linux':
                print('After', entry)


# if (entry['windows'] and entry['linux'] and entry['macos']):
# def ee(key):
#     return "-" if key is None else "X"
#     # print(f"{entry['command']: <50} {ee(entry['windows'])} {ee(entry['linux'])} {ee(entry['macos'])}")
# if not (entry['windows'] == entry['linux'] == entry['macos']):
#     print(f"{entry['command']: <50} {entry['windows']: <50} {entry['linux']: <50} {entry['macos']: <50}")

compare = ['windows', 'linux']
headers = compare + ['command'] + ['orig_' + h for h in compare]
table = []
for entry in entries:
    if (entry.get('windows') and entry.get('linux')):
        if not (entry.get('windows') == entry.get('linux')):
            table.append([entry.get(h) for h in headers])
            # print(f"{entry['command']: <50} {entry['windows']: <50} {entry['linux']: <50}")

print(tabulate(table, headers=headers))
# print(tabulate(table, headers=['command', 'windows', 'linux']))

for key in unmapped_vks:
    print(f"Unmapped VK: {key}")
