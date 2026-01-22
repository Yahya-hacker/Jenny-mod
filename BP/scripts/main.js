/**
 * Jenny Mod - UI Script
 * Uses @minecraft/server-ui for manual state selection
 * Implements MoLang State Machine UI with buttons for sequence control
 */
import { world, system } from '@minecraft/server';
import { ModalFormData, ActionFormData } from '@minecraft/server-ui';

/**
 * Button selection constants for maintainability
 */
const MenuButton = {
    SEQUENCE_ALPHA: 0,
    SEQUENCE_BETA: 1,
    RESET: 2
};

/**
 * Entity event constants
 */
const JennyEvent = {
    START_ALPHA: 'start_sequence_alpha',
    START_BETA: 'start_sequence_beta',
    RESET: 'reset_variant',
    ADVANCE: 'advance_sequence'
};

/**
 * Open the state selection menu for Jenny entity with button-based UI
 * @param {Player} player - The player opening the menu
 * @param {Entity} entity - The Jenny entity
 */
async function openStateMenu(player, entity) {
    const form = new ActionFormData()
        .title('§l§6Jenny - State Control')
        .body('§7Select an action to control animation sequences:')
        .button('§a Execute Sequence Alpha\n§7(Blowjob Animation)', 'textures/items/diamond')
        .button('§b Execute Sequence Beta\n§7(Doggy Animation)', 'textures/items/gold_ingot')
        .button('§c Initialize Reset\n§7(Return to Default)', 'textures/items/barrier');

    try {
        const response = await form.show(player);
        
        if (response.canceled || response.selection === undefined) {
            return;
        }

        switch (response.selection) {
            case MenuButton.SEQUENCE_ALPHA:
                entity.runCommand(`event entity @s ${JennyEvent.START_ALPHA}`);
                player.sendMessage('§a[Jenny] Started Sequence Alpha (Blowjob)');
                break;
            case MenuButton.SEQUENCE_BETA:
                entity.runCommand(`event entity @s ${JennyEvent.START_BETA}`);
                player.sendMessage('§b[Jenny] Started Sequence Beta (Doggy)');
                break;
            case MenuButton.RESET:
                entity.runCommand(`event entity @s ${JennyEvent.RESET}`);
                player.sendMessage('§c[Jenny] Reset to Default state');
                break;
        }
    } catch (error) {
        console.warn('[Jenny] Error showing menu:', error);
        player.sendMessage('§c[Jenny] Error: Could not open menu. Try again.');
    }
}

/**
 * Open advanced state selection with ModalFormData for more control
 * @param {Player} player - The player opening the menu
 * @param {Entity} entity - The Jenny entity
 */
async function openAdvancedMenu(player, entity) {
    const modal = new ModalFormData()
        .title('§l§6Jenny - Advanced Control')
        .dropdown(
            '§eSelect Animation Sequence:',
            [
                '0: Default (Idle/Walk)',
                '1: Sequence Alpha - Intro',
                '2: Sequence Alpha - Loop',
                '3: Sequence Alpha - Thrust',
                '4: Sequence Alpha - Outro',
                '5: Sequence Beta - Start',
                '6: Sequence Beta - Stage 1',
                '7: Sequence Beta - Stage 2',
                '8: Sequence Beta - Stage 3',
                '9: Sequence Beta - Finish'
            ],
            0
        )
        .toggle('§cForce Reset First', true);

    try {
        const response = await modal.show(player);
        
        if (response.canceled) {
            return;
        }

        const [sequenceChoice, forceReset] = response.formValues;
        
        // Reset first if toggle is on
        if (forceReset) {
            entity.runCommand('event entity @s reset_variant');
        }

        // Map dropdown selection to variant events
        const variantEvents = [
            'set_variant_0',
            'set_variant_1',
            'set_variant_2',
            'advance_sequence', // For variant 3, we need to be at 2 first
            'advance_sequence', // For variant 4, we need to be at 3 first
            'set_variant_5',
            'set_variant_6',
            'advance_sequence', // For variant 7
            'advance_sequence', // For variant 8
            'advance_sequence'  // For variant 9
        ];

        // Execute the event
        if (sequenceChoice <= 2 || sequenceChoice === 5 || sequenceChoice === 6) {
            entity.runCommand(`event entity @s ${variantEvents[sequenceChoice]}`);
        } else {
            // For higher variants, we need sequential advancement
            player.sendMessage('§6[Jenny] Use regular interactions to advance through stages');
        }

        player.sendMessage(`§a[Jenny] Set variant to ${sequenceChoice}`);
    } catch (error) {
        console.warn('[Jenny] Error showing advanced menu:', error);
        player.sendMessage('§c[Jenny] Error: Could not open menu');
    }
}

/**
 * Handle sneak-interact trigger via scriptevent
 */
function registerInteractionHandler() {
    // Listen for custom script events
    system.afterEvents.scriptEventReceive.subscribe((event) => {
        if (event.id === 'jenny:open_menu') {
            // Get the entity that sent the event and find nearby player
            const source = event.sourceEntity;
            
            if (!source) {
                console.warn('[Jenny] No source entity for scriptevent');
                return;
            }

            // Find the nearest player to open menu for
            const players = world.getAllPlayers();
            let nearestPlayer = null;
            let nearestDistance = Infinity;
            
            for (const player of players) {
                if (player.dimension.id !== source.dimension.id) continue;
                
                const dx = player.location.x - source.location.x;
                const dy = player.location.y - source.location.y;
                const dz = player.location.z - source.location.z;
                const distance = Math.sqrt(dx*dx + dy*dy + dz*dz);
                
                if (distance < nearestDistance && distance <= 5) {
                    nearestDistance = distance;
                    nearestPlayer = player;
                }
            }
            
            if (nearestPlayer) {
                openStateMenu(nearestPlayer, source);
            }
        } else if (event.id === 'jenny:state_change') {
            // Handle state change notifications
            console.log(`[Jenny] State changed to: ${event.message}`);
        }
    });
}

/**
 * Alternative method: Check for sneak + interact manually
 */
function registerManualSneakInteract() {
    world.afterEvents.entityInteract.subscribe((event) => {
        const player = event.player;
        const entity = event.target;
        
        // Check if interacting with Jenny while sneaking
        if (entity.typeId === 'sexmod:jenny' && player.isSneaking) {
            // Use a system run to avoid UI timing issues
            system.run(() => {
                openStateMenu(player, entity);
            });
        }
    });
}

/**
 * Initialize the script
 */
function init() {
    console.log('[Jenny Mod] UI Script initialized');
    
    // Register handlers
    registerInteractionHandler();
    registerManualSneakInteract();
    
    // Delayed startup message (after world loads)
    system.runTimeout(() => {
        world.sendMessage('§a[Jenny Mod] Script loaded successfully!');
    }, 100);
}

// Initialize once on script load
init();
