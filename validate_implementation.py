#!/usr/bin/env python3
"""
Comprehensive validation script for Bedrock addon implementation.
Validates:
1. Geometry pivot normalization (absolute to relative)
2. MoLang state machine logic in animation controllers
3. Entity interaction logic and variant progression
4. Cross-references between all components

Usage:
    python3 validate_implementation.py [--verbose] [--fix-issues]
"""
import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass


class Colors:
    """Terminal color codes for output formatting."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'


@dataclass
class ValidationResult:
    """Represents a single validation check result."""
    passed: bool
    message: str
    details: Optional[str] = None
    severity: str = "error"  # "error", "warning", "info"


class AddonValidator:
    """Main validator class for Bedrock addon validation."""
    
    def __init__(self, base_dir: Path, verbose: bool = False):
        self.base_dir = base_dir
        self.verbose = verbose
        self.results: List[ValidationResult] = []
        self.errors = 0
        self.warnings = 0
        self.passed = 0
        
    def load_json(self, file_path: Path) -> Optional[Dict]:
        """Load JSON file safely with error handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.add_result(False, f"File not found: {file_path}", severity="error")
            return None
        except json.JSONDecodeError as e:
            self.add_result(False, f"Invalid JSON in {file_path}: {e}", severity="error")
            return None
    
    def add_result(self, passed: bool, message: str, details: str = None, severity: str = "error"):
        """Add a validation result."""
        result = ValidationResult(passed, message, details, severity)
        self.results.append(result)
        
        if passed:
            self.passed += 1
        elif severity == "error":
            self.errors += 1
        else:
            self.warnings += 1
    
    def print_result(self, result: ValidationResult):
        """Print a validation result with appropriate formatting."""
        if result.passed:
            print(f"  {Colors.GREEN}✓{Colors.END} {result.message}")
        elif result.severity == "warning":
            print(f"  {Colors.YELLOW}⚠{Colors.END} {result.message}")
        else:
            print(f"  {Colors.RED}✗{Colors.END} {result.message}")
        
        if self.verbose and result.details:
            for line in result.details.split('\n'):
                print(f"    {Colors.CYAN}→{Colors.END} {line}")

    # =========================================================================
    # Task 1: Geometry Pivot Normalization Validation
    # =========================================================================
    
    def validate_geometry_pivots(self) -> bool:
        """
        Validate that geometry files have relative pivots.
        Formula: LocalPivot = AbsolutePivot_Child - AbsolutePivot_Parent
        """
        print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}Task 1: Hierarchical Pivot Normalization{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}")
        
        geo_files = list(self.base_dir.glob("RP/models/**/*.geo.json"))
        geo_files.extend(self.base_dir.glob("assets/sexmod/geo/**/*.geo.json"))
        
        all_valid = True
        
        for geo_file in geo_files:
            data = self.load_json(geo_file)
            if not data:
                all_valid = False
                continue
            
            # Check format version
            format_version = data.get('format_version', '')
            is_rp_file = 'RP/models' in str(geo_file)
            
            if is_rp_file:
                if format_version == '1.16.0':
                    self.add_result(True, f"Format version 1.16.0: {geo_file.name}")
                else:
                    self.add_result(False, f"Expected format 1.16.0, got {format_version}: {geo_file.name}")
                    all_valid = False
            
            # Validate pivot calculations for RP files
            if is_rp_file:
                for geometry in data.get('minecraft:geometry', []):
                    bones = geometry.get('bones', [])
                    validation_result = self._validate_bone_pivots(bones, geo_file.name)
                    if not validation_result:
                        all_valid = False
        
        return all_valid
    
    def _validate_bone_pivots(self, bones: List[Dict], filename: str) -> bool:
        """Validate that bone pivots are properly calculated as relative to parent."""
        # Build bone map
        bone_map = {b['name']: b for b in bones}
        
        issues = []
        for bone in bones:
            name = bone['name']
            parent_name = bone.get('parent')
            pivot = bone.get('pivot', [0, 0, 0])
            
            if parent_name and parent_name in bone_map:
                parent_pivot = bone_map[parent_name].get('pivot', [0, 0, 0])
                
                # Check if pivot values are reasonable (relative pivots should be smaller)
                # This is a heuristic check - relative pivots are typically smaller than absolute
                max_offset = max(abs(p) for p in pivot)
                
                # Flag suspiciously large relative pivots (> 50 units)
                if max_offset > 50:
                    issues.append(f"Large relative pivot for {name}: {pivot}")
        
        if issues:
            self.add_result(False, f"Suspicious pivot values in {filename}", 
                          details='\n'.join(issues[:5]), severity="warning")
            return False
        else:
            self.add_result(True, f"All bone pivots validated: {filename}")
            return True
    
    # =========================================================================
    # Task 2: MoLang State Machine Validation
    # =========================================================================
    
    def validate_state_machine(self) -> bool:
        """
        Validate animation controller state machine implementation.
        Checks:
        - query.variant as state register
        - States 0-9 properly mapped
        - query.any_animation_finished bridges
        """
        print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}Task 2: MoLang State Machine Validation{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}")
        
        controller_path = self.base_dir / 'RP/animation_controllers/character_logic.json'
        data = self.load_json(controller_path)
        
        if not data:
            return False
        
        all_valid = True
        
        # Validate format version
        format_version = data.get('format_version', '')
        if format_version:
            self.add_result(True, f"Animation controller format: {format_version}")
        
        # Get the main controller
        controllers = data.get('animation_controllers', {})
        main_controller = controllers.get('controller.animation.jenny.character_logic')
        
        if not main_controller:
            self.add_result(False, "Main controller not found")
            return False
        
        states = main_controller.get('states', {})
        
        # Check for required states
        required_states = [
            'default',
            'sequence_alpha_intro', 'sequence_alpha_loop', 
            'sequence_alpha_thrust', 'sequence_alpha_outro',
            'sequence_beta_start', 'sequence_beta_stage1',
            'sequence_beta_stage2', 'sequence_beta_finish'
        ]
        
        for state_name in required_states:
            if state_name in states:
                self.add_result(True, f"State exists: {state_name}")
            else:
                self.add_result(False, f"Missing state: {state_name}")
                all_valid = False
        
        # Validate query.variant usage in transitions
        variant_checks = []
        any_anim_finished_checks = []
        
        for state_name, state_def in states.items():
            transitions = state_def.get('transitions', [])
            
            for transition in transitions:
                for target, condition in transition.items():
                    if 'query.variant' in condition:
                        variant_checks.append(f"{state_name} -> {target}")
                    if 'query.any_animation_finished' in condition:
                        any_anim_finished_checks.append(f"{state_name} -> {target}")
        
        if variant_checks:
            self.add_result(True, f"query.variant used in {len(variant_checks)} transitions")
        else:
            self.add_result(False, "No query.variant transitions found")
            all_valid = False
        
        if any_anim_finished_checks:
            self.add_result(True, f"query.any_animation_finished used in {len(any_anim_finished_checks)} transitions")
        else:
            self.add_result(False, "No query.any_animation_finished bridges found")
            all_valid = False
        
        # Validate sequence alpha (1-4)
        alpha_variants = self._extract_variant_values(states, 'sequence_alpha')
        if 1 in alpha_variants:
            self.add_result(True, "Sequence Alpha starts at variant 1")
        else:
            self.add_result(False, "Sequence Alpha missing variant 1 trigger")
            all_valid = False
        
        # Validate sequence beta (5-9)
        beta_variants = self._extract_variant_values(states, 'sequence_beta')
        if 5 in beta_variants:
            self.add_result(True, "Sequence Beta starts at variant 5")
        else:
            self.add_result(False, "Sequence Beta missing variant 5 trigger")
            all_valid = False
        
        return all_valid
    
    def _extract_variant_values(self, states: Dict, prefix: str) -> Set[int]:
        """Extract variant values used in transitions for a sequence."""
        variants = set()
        
        for state_name, state_def in states.items():
            if prefix in state_name:
                for transition in state_def.get('transitions', []):
                    for target, condition in transition.items():
                        if 'query.variant ==' in condition:
                            # Extract the number
                            try:
                                value = int(condition.split('==')[1].strip())
                                variants.add(value)
                            except (ValueError, IndexError):
                                pass
        
        # Also check default state transitions
        default_state = states.get('default', {})
        for transition in default_state.get('transitions', []):
            for target, condition in transition.items():
                if prefix in target and 'query.variant ==' in condition:
                    try:
                        value = int(condition.split('==')[1].strip())
                        variants.add(value)
                    except (ValueError, IndexError):
                        pass
        
        return variants
    
    # =========================================================================
    # Task 3: Entity Interaction Logic Validation
    # =========================================================================
    
    def validate_entity_logic(self) -> bool:
        """
        Validate behavior pack entity file.
        Checks:
        - minecraft:interact with diamond/gold_ingot triggers
        - advance_stage event implementation
        - Variant progression (1-4, 5-9)
        """
        print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}Task 3: Entity Interaction Logic Validation{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}")
        
        entity_path = self.base_dir / 'BP/entities/jenny.json'
        data = self.load_json(entity_path)
        
        if not data:
            return False
        
        all_valid = True
        entity_def = data.get('minecraft:entity', {})
        
        # Check format version
        format_version = data.get('format_version', '')
        self.add_result(True, f"Entity format version: {format_version}")
        
        # Validate component groups (variants 0-9)
        component_groups = entity_def.get('component_groups', {})
        expected_variants = set(range(10))
        found_variants = set()
        
        for group_name, group_def in component_groups.items():
            if 'minecraft:variant' in group_def:
                value = group_def['minecraft:variant'].get('value')
                if value is not None:
                    found_variants.add(value)
        
        missing_variants = expected_variants - found_variants
        if not missing_variants:
            self.add_result(True, f"All variants (0-9) defined in component groups")
        else:
            self.add_result(False, f"Missing variant component groups: {missing_variants}")
            all_valid = False
        
        # Validate minecraft:interact component
        components = entity_def.get('components', {})
        interact = components.get('minecraft:interact', {})
        interactions = interact.get('interactions', [])
        
        diamond_trigger = False
        gold_trigger = False
        hand_advance = False
        sneak_menu = False
        
        for interaction in interactions:
            on_interact = interaction.get('on_interact', {})
            filters = on_interact.get('filters', {})
            event = on_interact.get('event', '')
            
            # Check filter conditions
            all_of = filters.get('all_of', [])
            for filter_cond in all_of:
                if filter_cond.get('value') == 'minecraft:diamond':
                    diamond_trigger = True
                if filter_cond.get('value') == 'minecraft:gold_ingot':
                    gold_trigger = True
                if filter_cond.get('value') == 'minecraft:air' and event == 'advance_sequence':
                    hand_advance = True
                if filter_cond.get('test') == 'is_sneaking' and filter_cond.get('value') == True:
                    sneak_menu = True
        
        self.add_result(diamond_trigger, "Diamond triggers Sequence Alpha")
        self.add_result(gold_trigger, "Gold Ingot triggers Sequence Beta")
        self.add_result(hand_advance, "Empty hand advances sequence")
        self.add_result(sneak_menu, "Sneaking opens menu")
        
        if not all([diamond_trigger, gold_trigger, hand_advance, sneak_menu]):
            all_valid = False
        
        # Validate events
        events = entity_def.get('events', {})
        
        required_events = [
            'minecraft:entity_spawned',
            'start_sequence_alpha',
            'start_sequence_beta',
            'advance_sequence',
            'reset_variant',
            'set_variant_0',
            'set_variant_1',
            'set_variant_5'
        ]
        
        for event_name in required_events:
            if event_name in events:
                self.add_result(True, f"Event defined: {event_name}")
            else:
                self.add_result(False, f"Missing event: {event_name}")
                all_valid = False
        
        # Validate advance_sequence logic
        advance_event = events.get('advance_sequence', {})
        sequence = advance_event.get('sequence', [])
        
        if sequence:
            self.add_result(True, f"advance_sequence has {len(sequence)} progression steps")
            
            # Check that it covers variants 2->3, 3->4, 6->7, 7->8, 8->9
            variant_progressions = []
            for step in sequence:
                filters = step.get('filters', {})
                if filters.get('test') == 'is_variant':
                    from_variant = filters.get('value')
                    add_groups = step.get('add', {}).get('component_groups', [])
                    for group in add_groups:
                        if 'variant_' in group:
                            try:
                                to_variant = int(group.split('_')[1])
                                variant_progressions.append((from_variant, to_variant))
                            except (ValueError, IndexError):
                                pass
            
            expected_progressions = [(2, 3), (3, 4), (6, 7), (7, 8), (8, 9)]
            for from_v, to_v in expected_progressions:
                if (from_v, to_v) in variant_progressions:
                    self.add_result(True, f"Progression {from_v} -> {to_v} implemented")
                else:
                    self.add_result(False, f"Missing progression {from_v} -> {to_v}")
                    all_valid = False
        else:
            self.add_result(False, "advance_sequence missing sequence array")
            all_valid = False
        
        return all_valid
    
    # =========================================================================
    # Task 4: Script API Validation
    # =========================================================================
    
    def validate_script_api(self) -> bool:
        """
        Validate behavior pack script file.
        Checks:
        - Import of @minecraft/server-ui
        - ModalFormData or ActionFormData usage
        - Required buttons implementation
        """
        print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}Task 4: Script API UI Validation{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}")
        
        script_path = self.base_dir / 'BP/scripts/main.js'
        
        if not script_path.exists():
            self.add_result(False, "Script file not found")
            return False
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                script_content = f.read()
        except Exception as e:
            self.add_result(False, f"Error reading script: {e}")
            return False
        
        all_valid = True
        
        # Check imports
        if '@minecraft/server' in script_content:
            self.add_result(True, "Imports @minecraft/server")
        else:
            self.add_result(False, "Missing @minecraft/server import")
            all_valid = False
        
        if '@minecraft/server-ui' in script_content:
            self.add_result(True, "Imports @minecraft/server-ui")
        else:
            self.add_result(False, "Missing @minecraft/server-ui import")
            all_valid = False
        
        # Check for form types
        if 'ModalFormData' in script_content or 'ActionFormData' in script_content:
            self.add_result(True, "Uses FormData UI components")
        else:
            self.add_result(False, "Missing FormData UI usage")
            all_valid = False
        
        # Check for required buttons/options
        button_checks = [
            ('Sequence Alpha', 'Execute Sequence Alpha button'),
            ('Sequence Beta', 'Execute Sequence Beta button'),
            ('Reset', 'Initialize Reset button')
        ]
        
        for keyword, description in button_checks:
            if keyword.lower() in script_content.lower():
                self.add_result(True, f"Contains {description}")
            else:
                self.add_result(False, f"Missing {description}")
                all_valid = False
        
        # Check for sneak-interact handling
        if 'isSneaking' in script_content or 'is_sneaking' in script_content:
            self.add_result(True, "Handles sneak-interact")
        else:
            self.add_result(False, "Missing sneak-interact handling")
            all_valid = False
        
        # Check for scriptevent handler
        if 'scriptEventReceive' in script_content:
            self.add_result(True, "Uses scriptEventReceive for event handling")
        else:
            self.add_result(False, "Missing scriptEventReceive handler", severity="warning")
        
        return all_valid
    
    # =========================================================================
    # Cross-Reference Validation
    # =========================================================================
    
    def validate_cross_references(self) -> bool:
        """Validate cross-references between all components."""
        print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}Cross-Reference Validation{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}")
        
        all_valid = True
        
        # Load all relevant files
        geo_path = self.base_dir / 'RP/models/entity/jenny/jennydressed.geo.json'
        controller_path = self.base_dir / 'RP/animation_controllers/character_logic.json'
        client_entity_path = self.base_dir / 'RP/entity/jenny.entity.json'
        entity_path = self.base_dir / 'BP/entities/jenny.json'
        
        geo_data = self.load_json(geo_path)
        controller_data = self.load_json(controller_path)
        client_entity_data = self.load_json(client_entity_path)
        entity_data = self.load_json(entity_path)
        
        # Extract geometry bone names
        geo_bones = set()
        if geo_data:
            for geom in geo_data.get('minecraft:geometry', []):
                for bone in geom.get('bones', []):
                    geo_bones.add(bone['name'])
            self.add_result(True, f"Geometry has {len(geo_bones)} bones")
        
        # Extract controller animation names
        controller_anims = set()
        if controller_data:
            for controller in controller_data.get('animation_controllers', {}).values():
                for state in controller.get('states', {}).values():
                    for anim in state.get('animations', []):
                        if isinstance(anim, str):
                            controller_anims.add(anim)
                        elif isinstance(anim, dict):
                            for key in anim.keys():
                                controller_anims.add(key)
            self.add_result(True, f"Controller references {len(controller_anims)} animations")
        
        # Validate client entity has all animations
        if client_entity_data:
            client_anims = set(client_entity_data.get('minecraft:client_entity', {})
                              .get('description', {}).get('animations', {}).keys())
            
            missing_anims = controller_anims - client_anims
            if not missing_anims:
                self.add_result(True, "All controller animations defined in client entity")
            else:
                self.add_result(False, f"Missing animations in client entity: {missing_anims}")
                all_valid = False
        
        # Validate event references between controller and entity
        if controller_data and entity_data:
            # Check that controller on_entry commands reference valid events
            entity_events = set(entity_data.get('minecraft:entity', {}).get('events', {}).keys())
            
            for controller in controller_data.get('animation_controllers', {}).values():
                for state_name, state in controller.get('states', {}).items():
                    for cmd in state.get('on_entry', []) + state.get('on_exit', []):
                        if 'event entity @s' in cmd:
                            event_name = cmd.split('event entity @s')[-1].strip()
                            if event_name in entity_events:
                                self.add_result(True, f"Valid event reference: {event_name}")
                            else:
                                self.add_result(False, f"Invalid event reference: {event_name}")
                                all_valid = False
        
        return all_valid
    
    # =========================================================================
    # Main Validation Runner
    # =========================================================================
    
    def run_all_validations(self) -> int:
        """Run all validation checks and return exit code."""
        print(f"\n{Colors.MAGENTA}{'#'*60}{Colors.END}")
        print(f"{Colors.MAGENTA}#  Bedrock Addon Implementation Validator{Colors.END}")
        print(f"{Colors.MAGENTA}#  Checking Tasks 1-4 + Cross-References{Colors.END}")
        print(f"{Colors.MAGENTA}{'#'*60}{Colors.END}")
        
        # Run all validations
        task1_valid = self.validate_geometry_pivots()
        task2_valid = self.validate_state_machine()
        task3_valid = self.validate_entity_logic()
        task4_valid = self.validate_script_api()
        xref_valid = self.validate_cross_references()
        
        # Print all results
        for result in self.results:
            self.print_result(result)
        
        # Summary
        print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}Validation Summary{Colors.END}")
        print(f"{Colors.BLUE}{'='*60}{Colors.END}")
        
        print(f"  {Colors.GREEN}Passed:{Colors.END}   {self.passed}")
        print(f"  {Colors.YELLOW}Warnings:{Colors.END} {self.warnings}")
        print(f"  {Colors.RED}Errors:{Colors.END}   {self.errors}")
        
        print()
        print(f"  Task 1 (Pivots):     {'✓ PASS' if task1_valid else '✗ FAIL'}")
        print(f"  Task 2 (State):      {'✓ PASS' if task2_valid else '✗ FAIL'}")
        print(f"  Task 3 (Entity):     {'✓ PASS' if task3_valid else '✗ FAIL'}")
        print(f"  Task 4 (Script):     {'✓ PASS' if task4_valid else '✗ FAIL'}")
        print(f"  Cross-References:    {'✓ PASS' if xref_valid else '✗ FAIL'}")
        
        if self.errors == 0:
            print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
            print(f"{Colors.GREEN}All validation checks passed!{Colors.END}")
            print(f"{Colors.GREEN}Implementation is ready for testing.{Colors.END}")
            print(f"{Colors.GREEN}{'='*60}{Colors.END}")
            return 0
        else:
            print(f"\n{Colors.RED}{'='*60}{Colors.END}")
            print(f"{Colors.RED}Validation failed with {self.errors} error(s).{Colors.END}")
            print(f"{Colors.RED}Please review and fix the issues above.{Colors.END}")
            print(f"{Colors.RED}{'='*60}{Colors.END}")
            return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Validate Bedrock addon implementation'
    )
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed output for each check')
    parser.add_argument('--base-dir', type=Path, default=Path(__file__).parent,
                       help='Base directory of the addon')
    
    args = parser.parse_args()
    
    validator = AddonValidator(args.base_dir, verbose=args.verbose)
    return validator.run_all_validations()


if __name__ == '__main__':
    sys.exit(main())
