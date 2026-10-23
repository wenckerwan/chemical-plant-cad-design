#!/usr/bin/env python3
"""Offline, relocatable skill installer. Requires Python 3.9+ standard library."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import unquote

NAME = 'chemical-plant-cad-design'


def relative_path(text):
    """Reject traversal, drive paths and Windows alternate data streams."""
    if not isinstance(text, str) or not text or '\\' in text or ':' in text:
        raise ValueError('Invalid manifest path: ' + repr(text))
    p = PurePosixPath(text)
    if p.is_absolute() or any(part in ('', '.', '..') for part in text.split('/')):
        raise ValueError('Unsafe manifest path: ' + text)
    return p


def files_below(root):
    result = {}
    for p in root.rglob('*'):
        if p.is_symlink() or (hasattr(p, 'is_junction') and p.is_junction()):
            raise ValueError('Links are not allowed in an installation tree: ' + str(p))
        if p.is_file():
            resolved = p.resolve()
            if not resolved.is_relative_to(root.resolve()):
                raise ValueError('File escapes installation tree: ' + str(p))
            result[p.relative_to(root).as_posix()] = p.read_bytes()
    return result


def validate_links(payload):
    for name, content in payload.items():
        if not name.endswith('.md'):
            continue
        text = content.decode('utf-8-sig')
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
            if target.startswith(('https://', 'http://', 'mailto:', '#')):
                continue
            target = unquote(target.split('#', 1)[0])
            if not target:
                continue
            if '\\' in target or ':' in target or target.startswith('/'):
                raise ValueError('Nonportable reference in ' + name + ': ' + target)
            parts = list(PurePosixPath(name).parent.parts)
            for part in PurePosixPath(target).parts:
                if part == '..':
                    if not parts:
                        raise ValueError('Reference escapes skill: ' + target)
                    parts.pop()
                elif part != '.':
                    parts.append(part)
            if '/'.join(parts) not in payload:
                raise ValueError('Broken skill reference in ' + name + ': ' + target)


def read_package(root):
    manifest_path = root / 'manifest.json'
    info = json.loads(manifest_path.read_text(encoding='utf-8'))
    if info.get('format') != 1 or info.get('skill_name') != NAME:
        raise ValueError('Unsupported package manifest')
    hashes = info.get('files')
    if not isinstance(hashes, dict) or not hashes:
        raise ValueError('Manifest has no files')
    actual = files_below(root)
    actual.pop('manifest.json', None)
    for name, digest in hashes.items():
        relative_path(name)
        if not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest):
            raise ValueError('Invalid digest for ' + name)
    if set(actual) != set(hashes):
        raise ValueError('Package file list differs from manifest; use an unmodified release copy')
    for name, content in actual.items():
        if hashlib.sha256(content).hexdigest() != hashes[name]:
            raise ValueError('Checksum mismatch: ' + name)
    prefix = 'skills/' + NAME + '/'
    payload = {name[len(prefix):]: data for name, data in actual.items() if name.startswith(prefix)}
    if 'SKILL.md' not in payload:
        raise ValueError('Missing skill entrypoint')
    text = payload['SKILL.md'].decode('utf-8-sig')
    frontmatter = re.match(r'^---\r?\n(.*?)\r?\n---(?:\r?\n|$)', text, re.S)
    if not frontmatter or not re.search(r'^name:\s*'+re.escape(NAME)+r'\s*$', frontmatter.group(1), re.M):
        raise ValueError('Skill name or frontmatter is invalid')
    validate_links(payload)
    return info, payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', choices=('agents', 'codex'), default='agents', help='agents: ~/.agents/skills (default); codex: CODEX_HOME/skills or ~/.codex/skills')
    parser.add_argument('--target', type=Path, help='Parent skills directory; the named skill folder is appended')
    parser.add_argument('--dry-run', action='store_true', help='Verify package and show target without writing')
    parser.add_argument('--verify-only', action='store_true', help='Verify release checksums and skill references without installing')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    info, payload = read_package(root)
    if args.verify_only:
        return {'status': 'verified', 'version': info['version'], 'skill_files': len(payload)}
    if args.target:
        parent = args.target.expanduser().resolve()
    elif args.profile == 'codex':
        configured = os.environ.get('CODEX_HOME')
        parent = ((Path(configured).expanduser() if configured else Path.home() / '.codex') / 'skills').resolve()
    else:
        parent = (Path.home() / '.agents' / 'skills').resolve()
    destination = parent / NAME
    if destination.is_relative_to(root) or root.is_relative_to(destination):
        raise ValueError('Destination must be outside the source package')
    if destination.is_symlink() or (hasattr(destination, 'is_junction') and destination.is_junction()):
        raise ValueError('Existing destination is a link; nothing was changed')
    if destination.exists():
        if destination.is_dir() and files_below(destination) == payload:
            return {'status': 'unchanged', 'destination': str(destination), 'version': info['version']}
        raise FileExistsError('Destination already exists and differs; back it up or choose another --target. Nothing was overwritten: ' + str(destination))
    if args.dry_run:
        return {'status': 'dry-run', 'destination': str(destination), 'version': info['version'], 'skill_files': len(payload)}
    parent.mkdir(parents=True, exist_ok=True)
    # Exclusive directory creation prevents overwriting a concurrent install.
    destination.mkdir(exist_ok=False)
    try:
        for name, content in payload.items():
            target = destination.joinpath(*relative_path(name).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream:
                stream.write(content)
        if files_below(destination) != payload:
            raise OSError('Installed bytes differ from the verified payload')
    except Exception as exc:
        # Preserve diagnostics and existing data; never recursively delete a user path.
        raise OSError('Installation incomplete at '+str(destination)+'; inspect this new folder before retrying: '+str(exc)) from exc
    return {'status': 'installed', 'destination': str(destination), 'version': info['version'], 'skill_files': len(payload)}


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')
    try:
        print(json.dumps(main(), ensure_ascii=False))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'error', 'message': str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
