import re
import sys

def clean_text(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the start of the first chapter
    start_idx = content.find('第一章')
    # Find the end of the 81st chapter (before the comments section)
    end_idx = content.find('编辑于 2021-08-16 04:11')
    
    if start_idx == -1 or end_idx == -1:
        print("Could not find start or end index")
        return
        
    text = content[start_idx:end_idx].strip()
    
    # Clean up empty lines
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line:
            cleaned_lines.append(line)
            
    # Re-format with nice spacing
    final_text = ""
    for i, line in enumerate(cleaned_lines):
        if re.match(r'^第[一二三四五六七八九十百]+章$', line):
            if i > 0:
                final_text += "\n\n"
            final_text += f"## {line}\n\n"
        elif line.startswith('【解释】'):
            final_text += f"\n**{line}**\n\n"
        else:
            final_text += f"{line}\n"
            
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 道德经 (Tao Te Ching) - 全文及释译\n\n")
        f.write("包含老子《道德经》全81章的文言文原文及白话文解释。\n\n")
        f.write(final_text)
        
    print(f"Successfully cleaned text and saved to {output_file}")

if __name__ == '__main__':
    clean_text(sys.argv[1], sys.argv[2])
