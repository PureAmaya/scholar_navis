'''
Original Author: gpt_academic@binary-husky

Modified by PureAmaya on 2025-04-11
- Output in English only.

Modified by PureAmaya on 2025-03-19
- Remove unused imports.
- Add internationalization support.
- Add exception handling for zip decompression.

Modified by PureAmaya on 2024-12-28
- Fix the issue of possible garbled characters when extracting compressed files.
'''
import os
import zipfile
import tarfile
import shutil

def html_local_file(file):
    base_path = os.path.dirname(__file__)  # 项目目录
    if os.path.exists(str(file)):
        file = f'file={file.replace(base_path, ".")}'
    return file


def html_local_img(__file, layout="left", max_width=None, max_height=None, md=True):
    style = ""
    if max_width is not None:
        style += f"max-width: {max_width};"
    if max_height is not None:
        style += f"max-height: {max_height};"
    __file = html_local_file(__file)
    a = f'<div align="{layout}"><img src="{__file}" style="{style}"></div>'
    if md:
        a = f"![{__file}]({__file})"
    return a


def file_manifest_filter_type(file_list, filter_: list = None):
    new_list = []
    if not filter_:
        filter_ = ["png", "jpg", "jpeg"]
    for file in file_list:
        if str(os.path.basename(file)).split(".")[-1] in filter_:
            new_list.append(html_local_img(file, md=False))
        else:
            new_list.append(file)
    return new_list


def zip_extract_member_new(self, member, targetpath, pwd):
    # 修复中文乱码的问题
    """Extract the ZipInfo object 'member' to a physical
        file on the path targetpath.
    """
    if not isinstance(member, zipfile.ZipInfo):
        member = self.getinfo(member)

    # build the destination pathname, replacing
    # forward slashes to platform specific separators.
    arcname = member.filename.replace('/', os.path.sep)
    arcname = arcname.encode('cp437', errors='replace').decode('gbk', errors='replace')

    if os.path.altsep:
        arcname = arcname.replace(os.path.altsep, os.path.sep)
    # interpret absolute pathname as relative, remove drive letter or
    # UNC path, redundant separators, "." and ".." components.
    arcname = os.path.splitdrive(arcname)[1]
    invalid_path_parts = ('', os.path.curdir, os.path.pardir)
    arcname = os.path.sep.join(x for x in arcname.split(os.path.sep)
                                if x not in invalid_path_parts)
    if os.path.sep == '\\':
        # filter illegal characters on Windows
        arcname = self._sanitize_windows_name(arcname, os.path.sep)

    targetpath = os.path.join(targetpath, arcname)
    targetpath = os.path.normpath(targetpath)

    # Create all upper directories if necessary.
    upperdirs = os.path.dirname(targetpath)
    if upperdirs and not os.path.exists(upperdirs):
        os.makedirs(upperdirs)

    if member.is_dir():
        if not os.path.isdir(targetpath):
            os.mkdir(targetpath)
        return targetpath

    with self.open(member, pwd=pwd) as source, \
            open(targetpath, "wb") as target:
        shutil.copyfileobj(source, target)

    return targetpath


def extract_archive(file_path, dest_dir):

    # Get the file extension of the input file
    file_extension = os.path.splitext(file_path)[1]

    # Extract the archive based on its extension
    if file_extension == ".zip":
        try:
            with zipfile.ZipFile(file_path, "r") as zipobj:
                #zipobj._extract_member = lambda a,b,c: zip_extract_member_new(zipobj, a,b,c)    # 修复中文乱码的问题
                zipobj.extractall(path=dest_dir)
                print("Successfully extracted zip archive to {}".format(dest_dir))
        except:
            print("Failed to extract zip archive to {}".format(dest_dir))
            return '\n\n{}'.format('Decompression failed! Please check if the compressed file is corrupted.')
        
    elif file_extension in [".tar", ".gz", ".bz2"]:
        with tarfile.open(file_path, "r:*") as tarobj:
            # 清理提取路径，移除任何不安全的元素
            for member in tarobj.getmembers():
                member_path = os.path.normpath(member.name)
                full_path = os.path.join(dest_dir, member_path)
                full_path = os.path.abspath(full_path)
                if not full_path.startswith(os.path.abspath(dest_dir) + os.sep):
                    raise Exception(f"Attempted Path Traversal in {member.name}")

            tarobj.extractall(path=dest_dir)
            print("Successfully extracted tar archive to {}".format(dest_dir))

    # 第三方库，需要预先pip install rarfile
    # 此外，Windows上还需要安装winrar软件，配置其Path环境变量，如"C:\Program Files\WinRAR"才可以
    elif file_extension == ".rar":
        try:
            import rarfile

            with rarfile.RarFile(file_path) as rf:
                rf.extractall(path=dest_dir)
                print("Successfully extracted rar archive to {}".format(dest_dir))
        except:
            print("Rar format requires additional dependencies to install")
            return '\n\n{}'.format('Extraction failed! You need to install pip install rarfile to extract RAR files. Suggestion: Use the ZIP compression format.')

    # 第三方库，需要预先pip install py7zr
    elif file_extension == ".7z":
        try:
            import py7zr

            with py7zr.SevenZipFile(file_path, mode="r") as f:
                f.extractall(path=dest_dir)
                print("Successfully extracted 7z archive to {}".format(dest_dir))
        except:
            print("7z format requires additional dependencies to install")
            return "\n\n解压失败! 需要安装pip install py7zr来解压7z文件"
    else:
        return ""
    return ""

