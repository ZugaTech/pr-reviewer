import re
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class DiffLine:
    type: str  # "added", "removed", "context"
    line_number_new: Optional[int]
    line_number_old: Optional[int]
    content: str

@dataclass
class Hunk:
    old_start: int
    old_count: int
    new_start: int
    new_count: int
    lines: List[DiffLine]

@dataclass
class FileDiff:
    filename: str
    language: str
    status: str  # "added", "modified", "deleted", "renamed"
    old_filename: Optional[str]
    hunks: List[Hunk]

def get_language(filename: str) -> str:
    ext = filename.split('.')[-1].lower() if '.' in filename else ""
    mapping = {
        'py': 'python',
        'js': 'javascript',
        'ts': 'typescript',
        'tsx': 'typescriptreact',
        'jsx': 'javascriptreact',
        'go': 'go',
        'java': 'java',
        'cpp': 'cpp',
        'c': 'c',
        'rs': 'rust',
        'rb': 'ruby',
        'php': 'php',
        'cs': 'csharp',
        'swift': 'swift',
        'sh': 'shell'
    }
    return mapping.get(ext, 'text')

def parse_diff(diff_str: str) -> List[FileDiff]:
    file_diffs = []
    # Split by "diff --git"
    raw_files = re.split(r'^diff --git ', diff_str, flags=re.MULTILINE)[1:]

    for raw_file in raw_files:
        lines = raw_file.splitlines()
        if not lines:
            continue

        # Extract filename (simple version)
        filename_match = re.search(r'b/(.+)$', lines[0])
        filename = filename_match.group(1) if filename_match else "unknown"
        
        status = "modified"
        if any(l.startswith("new file mode") for l in lines): status = "added"
        elif any(l.startswith("deleted file mode") for l in lines): status = "deleted"
        elif any(l.startswith("rename from") for l in lines): status = "renamed"

        hunks = []
        current_hunk = None
        new_line_ptr = 0
        old_line_ptr = 0

        for line in lines:
            if line.startswith("@@"):
                match = re.search(r'@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@', line)
                if match:
                    old_start = int(match.group(1))
                    old_count = int(match.group(2)) if match.group(2) else 1
                    new_start = int(match.group(3))
                    new_count = int(match.group(4)) if match.group(4) else 1
                    
                    current_hunk = Hunk(old_start, old_count, new_start, new_count, [])
                    hunks.append(current_hunk)
                    new_line_ptr = new_start
                    old_line_ptr = old_start
                    continue
            
            if current_hunk is not None:
                if line.startswith("+") and not line.startswith("+++"):
                    current_hunk.lines.append(DiffLine("added", new_line_ptr, None, line[1:]))
                    new_line_ptr += 1
                elif line.startswith("-") and not line.startswith("---"):
                    current_hunk.lines.append(DiffLine("removed", None, old_line_ptr, line[1:]))
                    old_line_ptr += 1
                elif line.startswith(" "):
                    current_hunk.lines.append(DiffLine("context", new_line_ptr, old_line_ptr, line[1:]))
                    new_line_ptr += 1
                    old_line_ptr += 1

        file_diffs.append(FileDiff(
            filename=filename,
            language=get_language(filename),
            status=status,
            old_filename=None, # Simplified
            hunks=hunks
        ))

    return file_diffs
