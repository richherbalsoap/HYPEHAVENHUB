import os
import re

directories = [
    r'c:\Users\abc\Downloads\Attached-Assets (1)\Attached-Assets\templates\store',
    r'c:\Users\abc\Downloads\Attached-Assets (1)\Attached-Assets\templates\auth'
]

icon_map = {
    'fa-search': 'search',
    'fa-heart': 'favorite',
    'fa-user': 'person',
    'fa-shopping-bag': 'shopping_bag',
    'fa-shopping-cart': 'shopping_bag',
    'fa-star': 'star',
    'fa-bars': 'menu',
    'fa-times': 'close',
    'fa-arrow-right': 'arrow_forward',
    'fa-arrow-left': 'arrow_back',
    'fa-chevron-right': 'chevron_right',
    'fa-chevron-left': 'chevron_left',
    'fa-plus': 'add',
    'fa-minus': 'remove',
    'fa-trash': 'delete',
    'fa-trash-alt': 'delete',
    'fa-edit': 'edit',
    'fa-check': 'check',
    'fa-check-circle': 'check_circle',
    'fa-eye': 'visibility',
    'fa-camera': 'photo_camera',
    'fa-lock': 'lock',
    'fa-shield-alt': 'verified_user',
    'fa-gem': 'diamond',
    'fa-truck': 'local_shipping',
    'fa-box': 'inventory_2',
    'fa-box-open': 'inventory_2',
    'fa-map-marker': 'location_on',
    'fa-map-marker-alt': 'location_on',
    'fa-phone': 'call',
    'fa-phone-alt': 'call',
    'fa-envelope': 'mail',
    'fa-key': 'key',
    'fa-cog': 'settings',
    'fa-gear': 'settings',
    'fa-bell': 'notifications',
    'fa-bell-slash': 'notifications_off',
    'fa-tag': 'sell',
    'fa-undo': 'undo',
    'fa-sign-out-alt': 'logout',
    'fa-spinner': 'progress_activity',
    'fa-share-alt': 'share',
    'fa-home': 'home',
    'fa-whatshot': 'whatshot',
    'fa-fire': 'whatshot',
    'fa-leaf': 'eco',
    'fa-hand-sparkles': 'auto_awesome',
    'fa-magnifying-glass': 'search'
}

def replace_icons(match):
    full_class = match.group(1)
    
    # Don't replace social media brand icons
    if 'fab ' in full_class or 'fa-instagram' in full_class or 'fa-facebook' in full_class or 'fa-youtube' in full_class or 'fa-pinterest' in full_class:
        return match.group(0)

    # Find the fa-* class
    fa_class_match = re.search(r'fa-[a-z-]+', full_class)
    if not fa_class_match:
        return match.group(0)
    
    fa_class = fa_class_match.group(0)
    if fa_class in icon_map:
        mat_icon = icon_map[fa_class]
        # Remove fas, far, fa, and the fa-xxx class
        new_class = re.sub(r'\b(fas|far|fa)\b', '', full_class)
        new_class = new_class.replace(fa_class, '')
        new_class = ' '.join(new_class.split()) # cleanup spaces
        
        if new_class:
            return f'<span class="material-symbols-outlined {new_class}">{mat_icon}</span>'
        else:
            return f'<span class="material-symbols-outlined">{mat_icon}</span>'
    
    # If the icon isn't in map but matches fa- format, log it or fallback
    return match.group(0)

files_updated = 0
for d in directories:
    for filename in os.listdir(d):
        if filename.endswith('.html') and filename not in ['home.html', 'checkout.html', 'cart.html']:
            filepath = os.path.join(d, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            orig_content = content
            
            # Replace icons
            content = re.sub(r'<i\s+class="([^"]*?fa-[^"]*?)"[^>]*></i>', replace_icons, content)
            
            # Replace specific old colors and classes
            content = content.replace('var(--pink)', 'var(--primary)')
            content = content.replace('var(--pink-deep)', 'var(--primary)')
            content = content.replace('var(--pink-pale)', 'var(--surface-container-low)')
            content = content.replace('var(--pink-light)', 'var(--surface-container)')
            
            content = content.replace('btn-pink', 'btn-artisan-primary')
            content = content.replace('btn-glamour-primary', 'btn-artisan-primary')
            content = content.replace('btn-glamour-outline', 'btn-artisan-outline')

            # Special case for complaints pages
            if filename in ['complaint_form.html', 'complaint_detail.html', 'complaints_list.html']:
                content = content.replace('btn btn-primary', 'btn btn-artisan-primary')
                content = content.replace('btn-outline-primary', 'btn-artisan-outline')
                content = content.replace('card shadow-sm', 'checkout-step')
                content = content.replace('alert alert-info', 'empty-state')
                content = content.replace('bg-info', 'bg-pink') # bg-pink is now mapped to primary in css
                
                # Remove purple focus style from complaint_form
                content = re.sub(r'<style>.*?#8B5CF6.*?</style>', '', content, flags=re.DOTALL)
            
            if content != orig_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_updated += 1
                print(f'Updated {filename}')

print(f"Total files updated: {files_updated}")
