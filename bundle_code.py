import os
import sqlite3

EXCLUDE_DIRS = {
    'venv', 'node_modules', '.pytest_cache', '__pycache__', '.git', 'dist', 'build', '.idea', '.vscode', 'uploads', 'v2_processed'
}

EXCLUDE_EXTENSIONS = {
    '.exe', '.db', '.sqlite', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.pdf', '.zip', '.tar', '.gz', '.7z', '.faiss', '.pkl'
}

EXCLUDE_FILES = {
    'medextract_source_code.txt', 'medextract_source_code_with_dumps.txt', 'cloudflared.exe', 'tesseract-installer.exe', 'package-lock.json'
}

DB_FILES = [
    'medextract.db',
    'medextract_backup_pre_session9.db',
    'test.db'
]

def is_text_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext in EXCLUDE_EXTENSIONS:
        return False
    return True

def get_db_dump(db_path):
    if not os.path.exists(db_path):
        return f"[Database file {db_path} not found]\n"
    try:
        conn = sqlite3.connect(db_path)
        dump_lines = list(conn.iterdump())
        conn.close()
        return "\n".join(dump_lines) + "\n"
    except Exception as e:
        return f"[Error dumping database {db_path}: {e}]\n"

def bundle_source_code(root_dir, output_file):
    collected_files = []
    
    for current_root, dirs, files in os.walk(root_dir):
        # Filter directories in place
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for f in files:
            if f in EXCLUDE_FILES:
                continue
            if is_text_file(f):
                full_path = os.path.join(current_root, f)
                rel_path = os.path.relpath(full_path, root_dir)
                collected_files.append((rel_path, full_path))
                
    collected_files.sort(key=lambda x: x[0])
    
    with open(output_file, 'w', encoding='utf-8', errors='replace') as out:
        out.write("# ================================================================================\n")
        out.write(f"# MedExtract Project - Complete Source Code & Database Dumps Bundle\n")
        out.write(f"# Total Source Files Included: {len(collected_files)}\n")
        out.write(f"# Total Database Dumps Included: {len(DB_FILES)}\n")
        out.write("# ================================================================================\n\n")
        
        # 1. Write Source Code Files
        out.write("# " + "=" * 78 + "\n")
        out.write("# SECTION 1: PROJECT SOURCE CODE FILES\n")
        out.write("# " + "=" * 78 + "\n\n")
        
        for rel_path, full_path in collected_files:
            out.write("=" * 80 + "\n")
            out.write(f"FILE: {rel_path}\n")
            out.write("=" * 80 + "\n\n")
            try:
                with open(full_path, 'r', encoding='utf-8', errors='replace') as infile:
                    content = infile.read()
                    out.write(content)
                    if not content.endswith('\n'):
                        out.write('\n')
            except Exception as e:
                out.write(f"[Error reading file: {e}]\n")
            out.write("\n\n")
            
        # 2. Write Database Dump Files
        out.write("# " + "=" * 78 + "\n")
        out.write("# SECTION 2: DATABASE DUMP FILES (SQL FORMAT)\n")
        out.write("# " + "=" * 78 + "\n\n")
        
        for db_name in DB_FILES:
            db_path = os.path.join(root_dir, db_name)
            out.write("=" * 80 + "\n")
            out.write(f"DATABASE DUMP: {db_name} (SQL Dump)\n")
            out.write("=" * 80 + "\n\n")
            dump_content = get_db_dump(db_path)
            out.write(dump_content)
            out.write("\n\n")
            
    print(f"Successfully generated {output_file} with {len(collected_files)} source files and {len(DB_FILES)} database dumps.")

if __name__ == '__main__':
    project_root = r'c:\Users\DELL\Desktop\Baja Finserv Health Pvt. Ltd\MedExtract'
    out_path = os.path.join(project_root, 'medextract_source_code.txt')
    bundle_source_code(project_root, out_path)

