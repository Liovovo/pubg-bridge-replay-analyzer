import argparse
import os
import sys

from PIL import Image

# Project: https://github.com/Liovovo/pubg-replay-data
# Based on: https://github.com/cgcostume/pubg-maps

def paste_image(img, target, target_x, target_y):
    """Paste image to target with proper format conversion."""
    img_width, img_height = img.size

    if img.mode == 'I':
        target.paste(img, (target_x, target_y))
    elif img.mode == 'RGB':
        r, g, b = img.split()
        r_arr = bytearray(r.tobytes())
        g_arr = bytearray(g.tobytes())
        height_bytes = bytearray(len(r_arr) * 2)
        for i in range(len(r_arr)):
            height_bytes[i * 2] = g_arr[i]
            height_bytes[i * 2 + 1] = r_arr[i]
        height_tile = Image.frombytes('I;16', (img_width, img_height), bytes(height_bytes))
        target.paste(height_tile, (target_x, target_y))
    elif img.mode == 'L':
        gray_arr = bytearray(img.tobytes())
        height_bytes = bytearray(len(gray_arr) * 2)
        for i in range(len(gray_arr)):
            height_bytes[i * 2] = 0
            height_bytes[i * 2 + 1] = gray_arr[i]
        height_tile = Image.frombytes('I;16', (img_width, img_height), bytes(height_bytes))
        target.paste(height_tile, (target_x, target_y))
    else:
        img_gray = img.convert('L')
        gray_arr = bytearray(img_gray.tobytes())
        height_bytes = bytearray(len(gray_arr) * 2)
        for i in range(len(gray_arr)):
            height_bytes[i * 2] = 0
            height_bytes[i * 2 + 1] = gray_arr[i]
        height_tile = Image.frombytes('I;16', (img_width, img_height), bytes(height_bytes))
        target.paste(height_tile, (target_x, target_y))


def process_map(map_identifier, config, umodel_base_path, output_path, compress, thumbnail):
    """Process a single map and export its heightmap."""
    map_width, map_height = config['size']
    num_tiles = map_width * map_height

    umodel_heightmap_path = os.path.abspath(os.path.join(umodel_base_path, config['path']))
    if not os.path.isdir(umodel_heightmap_path):
        print(f'Skipping {map_identifier}: path not found')
        return False

    print(f'\n=== Processing {map_identifier} ({map_width}x{map_height}) ===')
    print(f'Extracting heightmap tiles ...')

    # detect tile size from first available image
    tile_width = 512
    tile_height = 512
    for root, dirs, files in os.walk(umodel_heightmap_path):
        for fname in files:
            if fname.endswith('.png') and '_Heightmap_' in fname:
                try:
                    img = Image.open(os.path.join(root, fname))
                    tile_width, tile_height = img.size
                    img.close()
                    break
                except:
                    continue
        if tile_width != 512:
            break

    print(f'Detected tile size: {tile_width}x{tile_height}')

    height_composite = Image.new('I', (tile_width * map_width, tile_height * map_height))

    processed = 0
    rjust_len = len(str(num_tiles))

    offset_x = 1 if config.get('has_negative_coords') else 0
    offset_y = 1 if config.get('has_negative_coords') else 0

    if config['has_subfolders']:
        for x_block in range(4):
            for y_block in range(4):
                for sub_x in range(4):
                    for sub_y in range(4):
                        folder_name = config['folder_format'].format(
                            X=x_block, Y=y_block, sub_x=sub_x, sub_y=sub_y
                        )
                        folder_path = os.path.join(umodel_heightmap_path, folder_name)

                        if not os.path.isdir(folder_path):
                            continue

                        for fname in os.listdir(folder_path):
                            if not fname.endswith('.png') or '_Heightmap_' not in fname:
                                continue

                            parts = fname.replace('.png', '').split('_')
                            if len(parts) < 4 or parts[0] != 'Landscape':
                                continue

                            try:
                                global_x = int(parts[1]) + offset_x
                                global_y = int(parts[2]) + offset_y
                            except ValueError:
                                continue

                            if global_x < 0 or global_x >= map_width or global_y < 0 or global_y >= map_height:
                                continue

                            file_path = os.path.join(folder_path, fname)

                            try:
                                img = Image.open(file_path)
                            except Exception as e:
                                print(f'Error loading {file_path}: {e}')
                                continue

                            target_x = global_x * tile_width
                            target_y = global_y * tile_height

                            paste_image(img, height_composite, target_x, target_y)
                            img.close()

                            processed += 1
                            print(f'Processing {str(processed).rjust(rjust_len, "0")} tiles', flush=True, end='\r')
    else:
        grid_size_x = map_width // 2 if map_width % 2 == 0 else (map_width + 1) // 2
        grid_size_y = map_height // 2 if map_height % 2 == 0 else (map_height + 1) // 2

        for x in range(grid_size_x):
            for y in range(grid_size_y):
                folder_name = config['folder_format'].format(X=x, Y=y)
                folder_path = os.path.join(umodel_heightmap_path, folder_name)

                if not os.path.isdir(folder_path):
                    continue

                for fname in os.listdir(folder_path):
                    if not fname.endswith('.png') or '_Heightmap_' not in fname:
                        continue

                    parts = fname.replace('.png', '').split('_')
                    if len(parts) < 4 or parts[0] != 'Landscape':
                        continue

                    try:
                        global_x = int(parts[1]) + offset_x
                        global_y = int(parts[2]) + offset_y
                    except ValueError:
                        continue

                    if global_x < 0 or global_x >= map_width or global_y < 0 or global_y >= map_height:
                        continue

                    file_path = os.path.join(folder_path, fname)

                    try:
                        img = Image.open(file_path)
                    except Exception as e:
                        print(f'Error loading {file_path}: {e}')
                        continue

                    target_x = global_x * tile_width
                    target_y = global_y * tile_height

                    paste_image(img, height_composite, target_x, target_y)
                    img.close()

                    processed += 1
                    print(f'Processing {str(processed).rjust(rjust_len, "0")} tiles', flush=True, end='\r')

    print(f'\nProcessed {processed} tiles')

    if processed == 0:
        print(f'Warning: no tiles processed for {map_identifier}')
        return False

    map_size_descriptor = f'{map_width // 2}k'
    output_file = os.path.join(output_path, f'pubg_{map_identifier}_height_l16.png')
    print(f'Saving {map_size_descriptor} height map to {output_file} ...')
    height_composite.save(output_file, 'PNG', compress_level=min(9, compress), optimize=compress == 10)

    if thumbnail:
        thumb_file = os.path.join(output_path, f'pubg_{map_identifier}_height_preview.png')
        thumb = height_composite.copy()
        thumb.thumbnail((512, 512), Image.BICUBIC)
        thumb.save(thumb_file, 'PNG', compress_level=min(9, compress), optimize=compress == 10)

    print(f'{map_identifier} done!')
    return True


print('Project: https://github.com/Liovovo/pubg-replay-data')
print('Based on: https://github.com/cgcostume/pubg-maps')
print()

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--umodel_export_path', help='umodel export path', required=True)
parser.add_argument('-o', '--output_path', help='output directory', default='.')
parser.add_argument('-m', '--map', help='map identifier or "all" for all detected maps', default='all')
parser.add_argument('-c', '--compress', help='compression level 0-10', default='10')
parser.add_argument('-t', '--thumbnail', help='generate thumbnail', action='store_true')

args = parser.parse_args()

# all possible map configurations
map_configs = {
    'erangel': {
        'path': r'Game//Maps//Baltic//Art//HeightMap',
        'folder_format': 'Heightmap_x{X}_y{Y}_{sub_x}{sub_y}',
        'size': (16, 16),
        'has_subfolders': True,
    },
    'miramar': {
        'path': r'Game//Maps//Desert//Art//Heightmap',
        'folder_format': 'HeightMap_x{X}_y{Y}_{sub_x}{sub_y}',
        'size': (16, 16),
        'has_subfolders': True,
    },
    'sanhok': {
        'path': r'Game//Maps//Savage//Art//Heightmap',
        'folder_format': 'HeightMap_x{X}_y{Y}',
        'size': (8, 8),
        'has_subfolders': False,
    },
    'vikendi': {
        'path': r'Game//Maps//DihorOtok//Art//Heightmap',
        'folder_format': 'Heightmap_x{X}_y{Y}_{sub_x}{sub_y}',
        'size': (16, 16),
        'has_subfolders': True,
    },
    'karakin': {
        'path': r'Game//Maps//Summerland//Art//HeightMap',
        'folder_format': 'HeightMap_x{X}_y{Y}',
        'size': (4, 4),
        'has_subfolders': False,
    },
    'rondo': {
        'path': r'Game//Maps//Neon//Art//HeightMap',
        'folder_format': 'Heightmap_x{X}_y{Y}_{sub_x}{sub_y}',
        'size': (16, 16),
        'has_subfolders': True,
    },
    'deston': {
        'path': r'Game//Maps//Kiki//Art//HeightMap',
        'folder_format': 'HeightMap_x{X}_y{Y}_{sub_x}{sub_y}',
        'size': (16, 16),
        'has_subfolders': True,
    },
    'taego': {
        'path': r'Game//Maps//Tiger//Art//HeightMap',
        'folder_format': 'Heightmap_x{X}_y{Y}_{sub_x}{sub_y}',
        'size': (16, 16),
        'has_subfolders': True,
    },
    'paramo': {
        'path': r'Game//Maps//Chimera//Art//HeightMap',
        'folder_format': 'HeightMap_x{X}_y{Y}',
        'size': (6, 6),
        'has_subfolders': False,
    },
    'haven': {
        'path': r'Game//Maps//Heaven//Art//HeightMap',
        'folder_format': 'HeightMap_x{X}_y{Y}',
        'size': (5, 5),
        'has_subfolders': False,
        'has_negative_coords': True,
    },
}

output_path = args.output_path
if not os.path.isdir(output_path):
    os.makedirs(output_path)

compress = int(args.compress)

# determine which maps to process
if args.map.lower() == 'all':
    # auto-detect available maps
    available_maps = []
    for map_id, config in map_configs.items():
        map_path = os.path.abspath(os.path.join(args.umodel_export_path, config['path']))
        if os.path.isdir(map_path):
            available_maps.append(map_id)

    if not available_maps:
        sys.exit('No maps found in the specified path')

    print(f'Detected {len(available_maps)} map(s): {", ".join(available_maps)}')
    maps_to_process = available_maps
else:
    map_identifier = args.map.lower()
    if map_identifier not in map_configs:
        sys.exit(f'Unknown map: {map_identifier}')
    maps_to_process = [map_identifier]

# process all selected maps
success_count = 0
for map_id in maps_to_process:
    if process_map(map_id, map_configs[map_id], args.umodel_export_path, output_path, compress, args.thumbnail):
        success_count += 1

print(f'\n=== Summary ===')
print(f'Successfully processed {success_count} of {len(maps_to_process)} map(s)')
