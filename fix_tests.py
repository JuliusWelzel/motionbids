"""Quick script to add tracksys parameter to all MotionData instantiations in tests."""
import re

def fix_test_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match MotionData instantiations with tracked_points_count=10 but without tracksys
    # We'll add tracksys right after tracked_points_count
    pattern = r'(tracked_points_count=10)(\s*(?:,\s*\n\s*|\s*\)))'
    
    def replace_fn(match):
        if 'tracksys' not in content[max(0, match.start()-500):match.end()+500]:
            # Check if tracksys is NOT already in this MotionData call
            closing = match.group(2)
            if closing.strip() == ')':
                # No comma after, add tracksys with comma
                return match.group(1) + ',\n        tracksys="optical")'
            else:
                # Has comma, add tracksys
                return match.group(1) + ',\n        tracksys="optical"' + closing
        return match.group(0)
    
    # Find all MotionData blocks and add tracksys where needed
    # More robust: find lines with tracked_points_count=10 and add tracksys on next line if not present
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if 'tracked_points_count=10' in line and 'tracksys' not in line:
            # Check if tracksys is on the next few lines
            has_tracksys = False
            for j in range(i+1, min(i+10, len(lines))):
                if 'tracksys' in lines[j]:
                    has_tracksys = True
                    break
                if ')' in lines[j] and not has_tracksys:
                    break
            
            if not has_tracksys:
                # Add tracksys after this line
                fixed_lines.append(line)
                # Get the indentation
                indent = len(line) - len(line.lstrip())
                fixed_lines.append(' ' * indent + 'tracksys="optical",')
                i += 1
                continue
        
        fixed_lines.append(line)
        i += 1
    
    fixed_content = '\n'.join(fixed_lines)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    print(f"Fixed {filepath}")

if __name__ == '__main__':
    fix_test_file('tests/test_validator.py')
    fix_test_file('tests/test_exporter.py')
