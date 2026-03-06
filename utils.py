import re
from enum import Enum


def process_patch(patch, remove_test=True):
    """
    V4: Updated 04/10/2024
    04/17/2024: Update to leave better new lines between msg and files. Also change "Subject" to "Commit Message"
    """

    class PatchMinErrorType(Enum):
        EMPTY_CHANGE = 0
        NO_FILE_OF_INTEREST = 1
        ODD_FILE = 2
        FAIL = 3

    diff_command_regex = r"\ndiff --git [^@]+"
    diff_commands = re.findall(diff_command_regex, patch)
    patch_split = re.split(diff_command_regex, patch)
    # commit_id = re.findall(r"(?:^|\\n)From (\S+) Mon", patch_split[0])[0]
    header_info = "\n".join(patch_split[0].split("\n")[1:])
    header_info = header_info.split("\n---\n")[0]
    header_info = re.sub(
        "\nSubject: \[([^\]]+)\] ", "\nSubject: ", header_info)
    header_info = (
        "Commit Message: " +
        header_info.split("\nSubject: ")[-1].strip() + "\n"
    )
    file_changes = patch_split[1:]

    to_remove = []
    empty_changes = False
    for i, file_change in enumerate(file_changes):
        lines_changed = file_change.split("\n")
        modded_lines = ""
        for line in lines_changed:
            if line and line[0] in ["-", "+"]:
                modded_lines += line[1:].strip()
        if modded_lines.strip() == "":
            to_remove.append(i)
            empty_changes = True

    odd_file = False
    no_file = False
    file_names = []
    for diff_command in diff_commands:
        file_names.append(
            re.findall(
                r"\ndiff --git (?:\"|)a/(.+)\s(?:\"|)b/(.+)\n", diff_command)
        )

    for i, b_a_file_names in enumerate(file_names):
        if not b_a_file_names:
            to_remove.append(i)
            odd_file = True
            continue
        if remove_test and any(
            ["test" in file_name.lower() for file_name in b_a_file_names[0]]
        ):
            to_remove.append(i)
            continue

    new_patch = header_info
    for i in range(len(file_names)):
        if i in to_remove:
            continue
        new_patch += (
            "\n"
            + "a/"
            + file_names[i][0][0]
            + "\n"
            + "b/"
            + file_names[i][0][1]
            + "\n"
            + file_changes[i]
            + "\n"
        )

    error = None
    if "\na/" not in new_patch:
        if no_file:
            error = PatchMinErrorType(1)
        elif odd_file:
            error = PatchMinErrorType(2)
        elif empty_changes:
            error = PatchMinErrorType(0)
        else:
            error = PatchMinErrorType(3)
        return str(error)

    return new_patch.strip()
