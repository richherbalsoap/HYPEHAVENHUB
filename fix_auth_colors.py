import os
import glob

replacements = {
    '#faf6f0': 'var(--surface)',
    '#eae1d4': 'var(--surface-container)',
    'rgba(255, 255, 255, 0.9)': 'var(--surface-container-lowest)',
    'rgba(255, 255, 255, 0.8)': 'var(--outline-variant)',
    'background: #fff;': 'background: var(--surface-container-lowest);',
    'color: #fff;': 'color: var(--on-primary);',
    'color: #2d3748;': 'color: var(--on-surface);',
    'color: #6c757d;': 'color: var(--on-surface-variant);',
    'color: #4a5568;': 'color: var(--on-surface-variant);',
    'color: #718096;': 'color: var(--on-surface-variant);',
    'color: #a0aec0;': 'color: var(--outline);',
    'background-color: #fdf2f2;': 'background-color: var(--error-container);',
    'border: 1px solid #fbd5d5;': 'border: 1px solid var(--error);',
    'color: #9b1c1c;': 'color: var(--on-error-container);',
    'background: #fff"': 'background: var(--surface-container-lowest)"'
}

auth_dir = os.path.join('templates', 'auth')
for filepath in glob.glob(os.path.join(auth_dir, '*.html')):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Auth templates updated successfully!")
