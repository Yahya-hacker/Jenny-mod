#!/usr/bin/env python3
"""
Comprehensive validation script for Bedrock addon
Verifies all cross-references and JSON validity
"""
import json
import sys
from pathlib import Path
from typing import Dict, List, Set

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def validate_json_file(file_path: Path) -> bool:
    """Validate JSON syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        print(f"{Colors.GREEN}✓{Colors.END} {file_path.relative_to(file_path.parents[2])}")
        return True
    except json.JSONDecodeError as e:
        print(f"{Colors.RED}✗{Colors.END} {file_path.relative_to(file_path.parents[2])}: {e}")
        return False
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.END} {file_path}: {e}")
        return False

def load_json(file_path: Path) -> dict:
    """Load JSON file safely"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def check_cross_references(base_dir: Path) -> Dict[str, List[str]]:
    """Check cross-references between files"""
    issues = {}
    
    # Load files
    geo_path = base_dir / 'RP/models/entity/jenny/jennydressed.geo.json'
    anim_path = base_dir / 'RP/animations/jenny/jenny.animation.json'
    controller_path = base_dir / 'RP/animation_controllers/character_logic.json'
    client_entity_path = base_dir / 'RP/entity/jenny.entity.json'
    entity_path = base_dir / 'BP/entities/jenny.json'
    
    print(f"\n{Colors.BLUE}Cross-Reference Validation:{Colors.END}")
    
    # 1. Check geometry bones vs animation bones
    geo_data = load_json(geo_path)
    anim_data = load_json(anim_path)
    
    geo_bones = set()
    for geom in geo_data.get('minecraft:geometry', []):
        for bone in geom.get('bones', []):
            geo_bones.add(bone['name'])
    
    anim_bones = set()
    for anim_name, anim_def in anim_data.get('animations', {}).items():
        for bone_name in anim_def.get('bones', {}).keys():
            anim_bones.add(bone_name)
    
    missing_bones = anim_bones - geo_bones
    if missing_bones:
        issues['bones'] = list(missing_bones)
        print(f"  {Colors.RED}✗{Colors.END} Missing bones in geometry: {missing_bones}")
    else:
        print(f"  {Colors.GREEN}✓{Colors.END} All animation bones exist in geometry ({len(anim_bones)}/{len(geo_bones)})")
    
    # 2. Check animation controller references
    controller_data = load_json(controller_path)
    client_entity_data = load_json(client_entity_path)
    
    # Extract animation short names from controller
    controller_anims = set()
    for controller in controller_data.get('animation_controllers', {}).values():
        for state in controller.get('states', {}).values():
            for anim in state.get('animations', []):
                if isinstance(anim, str):
                    controller_anims.add(anim)
                elif isinstance(anim, dict):
                    for key in anim.keys():
                        controller_anims.add(key)
    
    # Check if they exist in client entity
    client_anims = set(client_entity_data.get('minecraft:client_entity', {})
                      .get('description', {}).get('animations', {}).keys())
    
    missing_anims = controller_anims - client_anims
    if missing_anims:
        issues['animations'] = list(missing_anims)
        print(f"  {Colors.RED}✗{Colors.END} Missing animations in client entity: {missing_anims}")
    else:
        print(f"  {Colors.GREEN}✓{Colors.END} All controller animations defined in client entity ({len(controller_anims)})")
    
    # 3. Check variant consistency
    entity_data = load_json(entity_path)
    component_groups = entity_data.get('minecraft:entity', {}).get('component_groups', {})
    
    variant_values = set()
    for group_name, group_def in component_groups.items():
        if 'minecraft:variant' in group_def:
            variant_values.add(group_def['minecraft:variant']['value'])
    
    expected_variants = set(range(10))  # 0-9
    missing_variants = expected_variants - variant_values
    
    if missing_variants:
        issues['variants'] = list(missing_variants)
        print(f"  {Colors.YELLOW}⚠{Colors.END} Missing variant values: {missing_variants}")
    else:
        print(f"  {Colors.GREEN}✓{Colors.END} All variant values (0-9) defined")
    
    return issues

def main():
    """Main validation function"""
    base_dir = Path(__file__).parent
    
    print(f"{Colors.BLUE}═══════════════════════════════════════════{Colors.END}")
    print(f"{Colors.BLUE}  Bedrock Addon Validation Suite{Colors.END}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════{Colors.END}")
    
    # 1. Validate JSON syntax
    print(f"\n{Colors.BLUE}JSON Syntax Validation:{Colors.END}")
    
    json_files = [
        base_dir / 'BP/manifest.json',
        base_dir / 'BP/entities/jenny.json',
        base_dir / 'RP/manifest.json',
        base_dir / 'RP/animation_controllers/character_logic.json',
        base_dir / 'RP/entity/jenny.entity.json',
        base_dir / 'RP/models/entity/jenny/jennydressed.geo.json',
        base_dir / 'RP/animations/jenny/jenny.animation.json',
    ]
    
    all_valid = True
    for json_file in json_files:
        if json_file.exists():
            if not validate_json_file(json_file):
                all_valid = False
        else:
            print(f"{Colors.RED}✗{Colors.END} File not found: {json_file}")
            all_valid = False
    
    # 2. Check cross-references
    issues = check_cross_references(base_dir)
    
    # 3. Final summary
    print(f"\n{Colors.BLUE}═══════════════════════════════════════════{Colors.END}")
    if all_valid and not issues:
        print(f"{Colors.GREEN}✓ All validation checks passed!{Colors.END}")
        print(f"\n{Colors.GREEN}Addon is ready for packaging and distribution.{Colors.END}")
        return 0
    else:
        print(f"{Colors.RED}✗ Validation failed with issues:{Colors.END}")
        for issue_type, issue_list in issues.items():
            print(f"  - {issue_type}: {issue_list}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
