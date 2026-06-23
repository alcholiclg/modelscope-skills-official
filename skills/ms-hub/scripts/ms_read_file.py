# /// script
# dependencies = ["modelscope>=1.34.0"]
# ///
"""
从 ModelScope 仓库下载并读取文件内容。

用法:
    uv run scripts/ms_read_file.py --repo_id "Qwen/Qwen2.5-7B-Instruct" --file_path "config.json"
    uv run scripts/ms_read_file.py --repo_id "modelscope/alpaca" --file_path "data/train.jsonl" --repo_type dataset
    uv run scripts/ms_read_file.py --repo_id "Qwen/Qwen2.5-7B-Instruct" --file_path "config.json" --max_lines 100
"""

import argparse
import mimetypes
import os
import sys


def is_text_file(file_path: str) -> bool:
    text_extensions = {
        '.txt', '.md', '.json', '.jsonl', '.csv', '.tsv', '.xml', '.yaml',
        '.yml', '.toml', '.ini', '.cfg', '.conf', '.py', '.js', '.ts',
        '.html', '.css', '.sh', '.bash', '.zsh', '.r', '.sql', '.log',
        '.gitignore', '.gitattributes', '.dockerfile', '.env',
    }
    _, ext = os.path.splitext(file_path.lower())
    if ext in text_extensions:
        return True

    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and mime_type.startswith('text/'):
        return True

    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(8192)
            if b'\x00' in chunk:
                return False
            return True
    except Exception:
        return False


def format_size(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f'{size_bytes:.1f} {unit}'
        size_bytes /= 1024
    return f'{size_bytes:.1f} TB'


def read_file(repo_id: str, file_path: str, repo_type: str = 'model',
              revision: str = 'master', max_lines: int = 500) -> str:
    try:
        if repo_type == 'dataset':
            from modelscope.hub.file_download import dataset_file_download
            local_path = dataset_file_download(
                dataset_id=repo_id,
                file_path=file_path,
                revision=revision,
            )
        else:
            from modelscope.hub.file_download import model_file_download
            local_path = model_file_download(
                model_id=repo_id,
                file_path=file_path,
                revision=revision,
            )
    except Exception as e:
        return f'错误：无法下载文件 {file_path}\n原因: {e}'

    file_size = os.path.getsize(local_path)
    header = f'文件: {repo_id}/{file_path} (revision: {revision})\n'
    header += f'大小: {format_size(file_size)}\n'

    if not is_text_file(local_path):
        header += f'类型: 二进制文件\n'
        header += '（二进制文件不显示内容）'
        return header

    header += '---\n'
    try:
        with open(local_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    lines.append(f'\n... (已截断，共显示 {max_lines} 行，文件总大小 {format_size(file_size)})')
                    break
                lines.append(line.rstrip('\n'))
            content = '\n'.join(lines)
    except Exception as e:
        content = f'读取错误: {e}'

    return header + content


def main():
    parser = argparse.ArgumentParser(description='从 ModelScope 仓库读取文件内容')
    parser.add_argument('--repo_id', required=True, help='仓库 ID (如 Qwen/Qwen2.5-7B-Instruct)')
    parser.add_argument('--file_path', required=True, help='文件路径 (如 config.json)')
    parser.add_argument('--repo_type', default='model', choices=['model', 'dataset'],
                        help='仓库类型 (默认: model)')
    parser.add_argument('--revision', default='master', help='分支/标签/SHA (默认: master)')
    parser.add_argument('--max_lines', type=int, default=500, help='最大读取行数 (默认: 500)')

    args = parser.parse_args()
    result = read_file(
        repo_id=args.repo_id,
        file_path=args.file_path,
        repo_type=args.repo_type,
        revision=args.revision,
        max_lines=args.max_lines,
    )
    print(result)


if __name__ == '__main__':
    main()
