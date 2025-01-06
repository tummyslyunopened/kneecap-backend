import os
import shutil


def get_directory_size(directory_path, relative=True):
    """
    Returns the total size (in GB) of all files in the given directory, rounded to 2 decimal places.

    :param directory_path: The path to the directory.
    :param relative: If True, convert the directory path to an absolute path.
    :return: Total size in GB, rounded to 2 decimal places.
    """
    if relative:
        directory_path = os.path.abspath(directory_path)
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.isfile(filepath):  # Check if it's a file
                total_size += os.path.getsize(filepath)
    # Convert total_size from bytes to GB and round to 2 decimal places
    total_size_gb = round(total_size / (1024**3), 2)
    return total_size_gb


def get_directory_size_non_recursive(directory_path, relative=True):
    """
    Returns the total size (in GB) of all files in the given directory (non-recursive), rounded to 2 decimal places.

    :param directory_path: The path to the directory.
    :param relative: If True, convert the directory path to an absolute path.
    :return: Total size in GB, rounded to 2 decimal places.
    """
    if relative:
        directory_path = os.path.abspath(directory_path)
    total_size = 0
    for filename in os.listdir(directory_path):
        filepath = os.path.join(directory_path, filename)
        if os.path.isfile(filepath):  # Check if it's a file
            total_size += os.path.getsize(filepath)
    # Convert total_size from bytes to GB and round to 2 decimal places
    total_size_gb = round(total_size / (1024**3), 2)
    return total_size_gb


def get_available_space(filepath, relative=True):
    """
    Returns the available space (in GB) on the disk where the given filepath is located, rounded to 2 decimal places.

    :param filepath: The path to the file.
    :param relative: If True, convert the file path to an absolute path.
    :return: Available space in GB, rounded to 2 decimal places.
    """
    if relative:
        filepath = os.path.abspath(filepath)

    # Get the disk usage of the drive containing the given filepath
    disk_usage = shutil.disk_usage(filepath)
    # Convert free space from bytes to GB and round to 2 decimal places
    free_space_gb = round(disk_usage.free / (1024**3), 2)
    return free_space_gb  # Return the free space in GB, rounded to 2 decimal places


def storage_summary(directory_path, relative=True):
    summary = {}
    for dir_name in os.listdir(directory_path):
        dir_path = os.path.join(directory_path, dir_name)
        if os.path.isdir(dir_path):
            summary[dir_name] = get_directory_size(dir_path, relative=False)
    summary["other"] = get_directory_size_non_recursive(directory_path, relative)
    return summary


# Example usage:
directory_path = "../media"  # Relative path for demonstration
print(storage_summary(directory_path, relative=True))
