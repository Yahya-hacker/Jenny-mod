Jenny Mod: Bedrock Edition Port (v1.0.0)
A high-fidelity technical port of the original "Jenny Mod" assets to Minecraft Bedrock Edition. This project utilizes a custom JSON-based State Machine to replicate complex Java-side behaviors and cinematic sequences without the need for external scripts.
🛠 Technical Overview
Unlike standard ports, this version focuses on Logical Mapping and Bone Hierarchy Realignment to ensure stability on the RenderDragon engine.
Core Architecture
 * State Machine (RP): Implemented via animation_controllers.json. It manages transitions between idle, intro, loop, and outro states using MoLang queries (query.anim_time and query.any_animation_finished).
 * Data-Driven Logic (BP): Uses the minecraft:variant component to track entity states. Interactions update the variant ID, which is then globally synced with the Resource Pack.
 * Geometry Realignment: The model hierarchy has been rebuilt from the original .jar assets. Pivots are normalized to a root -> body -> appendages structure to prevent "fragmentation" bugs common in mobile ports.
✨ Features
 * State-Linked Interactions:
   * Diamond: Triggers the Blowjob sequence.
   * Gold Ingot: Triggers the Doggy sequence.
   * Emerald: Triggers the Strip sequence.
 * Manual Scene Advancement: Use an Empty Hand to progress through multi-stage animations (Suck -> Thrust -> Finish).
 * RenderDragon Optimized: Uses entity_alphatest materials to support high-resolution textures and transparency layers without flickering.
📂 Project Structure
Jenny-mod/
├── BP/                         # Behavior Pack
│   ├── entities/               # Entity logic & Interaction components
│   ├── manifest.json           # Pack identity & Dependencies
│   └── pack_icon.png
└── RP/                         # Resource Pack
    ├── animations/             # Re-mapped .animation.json files
    ├── animation_controllers/  # The MoLang State Machine
    ├── entity/                 # Client-side entity definitions
    ├── models/entity/          # Optimized .geo.json geometry
    ├── textures/entity/        # Original high-res .png textures
    └── texts/                  # Localization (en_US.lang)

🚀 Installation & Usage
 * Download the latest .mcaddon from the Releases section (if available).
 * Import the pack into Minecraft PE / Bedrock.
 * Experimental Toggles Required:
   * Holiday Creator Features
   * Beta APIs (Optional, for future Script API support)
   * Molang Features
 * Enable both the Resource Pack and Behavior Pack in your world settings.
⚠️ Disclaimer
This project is a technical port intended for educational purposes in Reverse Engineering and Minecraft Add-on Development. All original assets belong to their respective creators.
