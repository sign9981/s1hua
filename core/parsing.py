# core/parsing.py
import re
import csv
import ipaddress
from pathlib import Path
from .utils import logger

def extract_hostname(raw: str) -> str:
    s = raw.strip().lower()
    if not s:
        return ""
    if s.startswith(('http://', 'https://')):
        s = s.split('://', 1)[1]
    s = s.split('/', 1)[0]
    s = s.split(':', 1)[0]
    if s.endswith('.'):
        s = s[:-1]
    return s

def is_valid_domain(s: str) -> bool:
    if not s or len(s) > 253:
        return False
    if s.startswith('-') or s.endswith('-') or '..' in s:
        return False
    try:
        ipaddress.ip_address(s)
        return False
    except ValueError:
        pass
    
    return re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?)*$', s) is not None

def _guess_domain_column(rows: list, max_sample_rows: int = 20) -> int:
    if not rows:
        return 0

    max_cols = max(len(row) for row in rows)
    if max_cols == 0:
        return 0

    score = [0] * max_cols
    count = [0] * max_cols

    for row in rows[:max_sample_rows]:
        for i, cell in enumerate(row):
            if i >= max_cols:
                break
            count[i] += 1
            cand = extract_hostname(cell.strip())
            if is_valid_domain(cand):
                score[i] += 1

    best_col, best_ratio = 0, 0.0
    for i in range(max_cols):
        ratio = score[i] / count[i] if count[i] > 0 else 0
        if ratio > best_ratio:
            best_ratio = ratio
            best_col = i

    return best_col if best_ratio > 0 else 0

def extract_subdomains(file_path: Path):
    subs = set()
    suffix = file_path.suffix.lower()

    try:
        if suffix == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    parts = line.strip().split()
                    if not parts:
                        continue
                    raw_value = parts[0]
                    candidate = extract_hostname(raw_value)
                    if is_valid_domain(candidate):
                        subs.add(candidate)
        elif suffix == '.csv':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [line.strip() for line in f if line.strip()]
                if not lines:
                    return set()

                sample = '\n'.join(lines[:2])
                try:
                    delimiter = csv.Sniffer().sniff(sample).delimiter
                except:
                    delimiter = ','

                reader = csv.reader(lines, delimiter=delimiter)
                all_rows = list(reader)
                if not all_rows:
                    return set()

                keywords = {'subdomain', 'host', 'domain', 'url', 'hostname', 'fqdn', 'site'}
                first_row_lower = [cell.lower() for cell in all_rows[0]]
                has_header = any(any(kw in cell for kw in keywords) for cell in first_row_lower)

                if has_header:
                    headers = all_rows[0]
                    data_rows = all_rows[1:]
                    subdomain_col_index = None
                    for i, h in enumerate(headers):
                        if any(kw in h.lower() for kw in keywords):
                            subdomain_col_index = i
                            break
                    if subdomain_col_index is None:
                        subdomain_col_index = _guess_domain_column(data_rows)
                else:
                    data_rows = all_rows
                    subdomain_col_index = _guess_domain_column(data_rows)

                for row in data_rows:
                    if subdomain_col_index < len(row):
                        raw_val = row[subdomain_col_index].strip()
                        if raw_val:
                            candidate = extract_hostname(raw_val)
                            if is_valid_domain(candidate):
                                subs.add(candidate)
        else:
            logger.warning(f"⚠️  不支持的文件格式: {file_path.suffix}，跳过解析")
            return set()

    except Exception as e:
        logger.error(f"❌ 解析文件失败 {file_path.name}: {e}")
        return set()

    return subs