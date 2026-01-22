# Bedrock Edition Technical Port - Implementation Guide

## Overview
This implementation refactors the Jenny mod for Minecraft Bedrock 1.21.132 with RenderDragon engine compatibility. All files follow the latest Bedrock addon specifications with proper state machine architecture.

## Architecture

### Resource Pack (RP/) Structure
```
RP/
├── manifest.json                               # Pack metadata & dependencies
├── models/entity/jenny/
│   └── jennydressed.geo.json                   # Format 1.16.0 with relative pivots
├── animations/jenny/
│   └── jenny.animation.json                    # Bone animations
├── animation_controllers/
│   └── character_logic.json                    # MoLang state machine
├── entity/
│   └── jenny.entity.json                       # Client-side entity definition
└── texts/
    └── en_US.lang                              # Localization strings
```

### Behavior Pack (BP/) Structure
```
BP/
├── manifest.json                               # Pack metadata with Script API deps
├── entities/
│   └── jenny.json                              # Entity logic & interactions
└── scripts/
    └── main.js                                 # UI scripting with @minecraft/server-ui
```

## Implementation Details

### Task 1: Geometry Format Update (1.12.0 → 1.16.0)
**File:** `RP/models/entity/jenny/jennydressed.geo.json`

**Changes Made:**
- ✅ Updated `format_version` from "1.12.0" to "1.16.0"
- ✅ Recalculated all 294 bone pivots using relative coordinates
  - Formula: `LocalPivot = AbsolutePivot_Child - AbsolutePivot_Parent`
  - Example: `upperBody` was [0, 11.1, 0] absolute → now [0, 11.1, 0] relative to body
  - Example: `torso` was [0, 16.1637, -1.803] absolute → now [0, 5.0637, -1.803] relative to upperBody
- ✅ Set `visible_bounds_width`: 3.0 (was 697)
- ✅ Set `visible_bounds_height`: 3.0 (was 696)
- ✅ Set `visible_bounds_offset`: [0, 1.5, 0] (was [0, 1, 0])

**Implementation:** Python script `convert_geometry.py` performs bulk mathematical operations on all bone pivots while preserving hierarchy.

### Task 2: Animation Cross-Reference
**Files:** 
- `RP/animations/jenny/jenny.animation.json`
- `RP/models/entity/jenny/jennydressed.geo.json`

**Changes Made:**
- ✅ Extracted 73 unique bone identifiers from animations
- ✅ Verified against 294 bones in geometry
- ✅ Added 8 missing placeholder bones:
  - `Rside` → parented to `hip`
  - `asshole` → parented to `hip`
  - `boobL` → parented to `torso`
  - `boobR` → parented to `torso`
  - `dd` → parented to `body`
  - `smugSmile` → parented to `head`
  - `turnable` → parented to `body`
  - `wideSmugSmile` → parented to `head`

**Implementation:** Python script `cross_reference_bones.py` automatically detects missing bones and adds them with logical parent relationships.

### Task 3: Animation Controller State Machine
**File:** `RP/animation_controllers/character_logic.json`

**State Definitions:**
| State | Variant | Animation | Transition |
|-------|---------|-----------|------------|
| `default` | 0 | idle/walk/run | Manual trigger to sequences |
| `sequence_alpha_intro` | 1 | blowjob_intro | Auto → loop |
| `sequence_alpha_loop` | 2 | blowjob_suck | Manual → thrust |
| `sequence_alpha_thrust` | 3 | blowjob_thrust | Manual → outro |
| `sequence_alpha_outro` | 4 | blowjob_cum | Auto → default |
| `sequence_beta_start` | 5 | doggy_start | Auto → stage1 |
| `sequence_beta_stage1` | 6 | doggy_slow | Manual → stage2 |
| `sequence_beta_stage2` | 7 | doggy_fast_soft | Manual → stage3 |
| `sequence_beta_stage3` | 8 | (intermediate) | Manual → finish |
| `sequence_beta_finish` | 9 | doggy_cum | Auto → default |

**MoLang Queries Used:**
- `query.variant` - State register (0-9)
- `query.any_animation_finished` - Automatic linear transitions
- `query.is_on_ground` - Movement detection
- `query.modified_move_speed` - Speed-based animation blending

### Task 4: Behavior Entity Definition
**File:** `BP/entities/jenny.json`

**Component Groups:**
- 10 variant groups (`variant_0_default` through `variant_9_beta_finish`)
- Each group sets `minecraft:variant` component to corresponding value

**Interaction System:**
| Item | Event | Result |
|------|-------|--------|
| Diamond | `start_sequence_alpha` | Sets variant to 1 (Blowjob intro) |
| Gold Ingot | `start_sequence_beta` | Sets variant to 5 (Doggy start) |
| Empty Hand | `advance_sequence` | Increments variant within sequence |
| Sneak + Interact | `open_menu` | Triggers script event for UI |

**Events:**
- `start_sequence_alpha` - Initialize blowjob sequence
- `start_sequence_beta` - Initialize doggy sequence
- `advance_sequence` - Progress through multi-stage animations
- `reset_variant` - Return to default state
- `set_variant_0/1/5` - Manual state jumps (for UI)
- `open_menu` - Script event to trigger modal UI

### Task 5: Script API UI
**File:** `BP/scripts/main.js`

**Features:**
- ✅ Import `@minecraft/server-ui` for ModalFormData
- ✅ Sneak-interact trigger detection
- ✅ Modal menu with:
  - Dropdown: Select sequence (Default/Alpha/Beta)
  - Toggle: Reset to default option
- ✅ Event dispatching to entity via `runCommand('event entity @s ...')`

**Usage:**
1. Player sneaks and interacts with Jenny
2. Modal opens with state selection
3. Player chooses sequence or reset
4. Script sends corresponding event to entity
5. Entity variant updates and animation controller responds

## Testing & Validation

### JSON Validation
All JSON files have been validated with `jq`:
- ✅ BP/manifest.json
- ✅ BP/entities/jenny.json
- ✅ RP/manifest.json
- ✅ RP/animation_controllers/character_logic.json
- ✅ RP/entity/jenny.entity.json
- ✅ RP/models/entity/jenny/jennydressed.geo.json (76,032 lines)
- ✅ RP/animations/jenny/jenny.animation.json (40,678 lines)

### Cross-Reference Verification
- ✅ All animation bone references exist in geometry
- ✅ Animation controller references match entity animations
- ✅ Entity events match animation controller states
- ✅ Variant values are consistent across all files

## Installation

### For Minecraft Bedrock Edition 1.21.132+:
1. Enable Experimental Features:
   - Holiday Creator Features
   - Beta APIs
   - Molang Features
2. Copy `RP/` folder to `<world>/resource_packs/`
3. Copy `BP/` folder to `<world>/behavior_packs/`
4. Activate both packs in world settings

### Development:
```bash
# Run geometry conversion
python3 convert_geometry.py

# Run bone cross-reference check
python3 cross_reference_bones.py

# Validate JSON files
find BP RP -name "*.json" -exec jq empty {} \;
```

## Technical Notes

### RenderDragon Compatibility
- Uses `entity_alphatest` material for transparency
- Visible bounds optimized to 3x3x3 for mobile performance
- Format 1.16.0 ensures compatibility with latest rendering pipeline

### State Machine Logic
- Linear transitions use `query.any_animation_finished`
- Manual progression via empty hand interact
- Automatic reset after sequence completion
- Fallback to default state on any error

### Script API Integration
- Uses @minecraft/server v1.8.0
- Uses @minecraft/server-ui v1.2.0
- Event-based communication between script and entity
- Alternative: Direct interaction detection without entity event

## Troubleshooting

### Issue: Animations not playing
- Verify animation names in `jenny.entity.json` match `jenny.animation.json`
- Check animation controller is in "animate" scripts array
- Confirm variant component is updating (use `/testfor`)

### Issue: Bones appear disconnected
- Verify pivot calculations in geometry file
- Check parent relationships are valid
- Ensure format_version is 1.16.0

### Issue: UI menu not opening
- Confirm Beta APIs experimental toggle is enabled
- Check script manifest dependencies
- Verify entity type ID is "sexmod:jenny"

## Credits
Geometry conversion and bone hierarchy refactoring performed via automated Python scripts with mathematical precision. All animations preserved from original Java mod assets.
