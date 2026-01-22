/**
 * Jenny Mod - UI Script
 * Uses @minecraft/server-ui for manual state selection
 */
import { world, system } from '@minecraft/server';
import { ModalFormData } from '@minecraft/server-ui';

/**
 * Open the state selection menu for Jenny entity
 * @param {Player} player - The player opening the menu
 * @param {Entity} entity - The Jenny entity
 */
async function openStateMenu(player, entity) {
    const modal = new ModalFormData()
        .title('§l§6Jenny - State Control')
        .dropdown(
            '§eSelect Animation Sequence:',
            [
                'Default (Idle/Walk)',
                'Sequence Alpha - Blowjob',
                'Sequence Beta - Doggy'
            ],
            0
        )
        .toggle('§cReset to Default', false);

    try {
        const response = await modal.show(player);
        
        if (response.canceled) {
            return;
        }

        const [sequenceChoice, shouldReset] = response.formValues;
        
        // Handle reset
        if (shouldReset) {
            entity.runCommand('event entity @s reset_variant');
            player.sendMessage('§aReset Jenny to default state');
            return;
        }

        // Handle sequence selection
        switch (sequenceChoice) {
            case 0: // Default
                entity.runCommand('event entity @s set_variant_0');
                player.sendMessage('§aSet to Default state');
                break;
            case 1: // Sequence Alpha
                entity.runCommand('event entity @s set_variant_1');
                player.sendMessage('§aStarted Sequence Alpha (Blowjob)');
                break;
            case 2: // Sequence Beta
                entity.runCommand('event entity @s set_variant_5');
                player.sendMessage('§aStarted Sequence Beta (Doggy)');
                break;
        }
    } catch (error) {
        console.warn('Error showing menu:', error);
        player.sendMessage('§cError: Could not open menu');
    }
}

/**
 * Handle sneak-interact trigger
 */
function registerInteractionHandler() {
    // Listen for custom script events
    system.afterEvents.scriptEventReceive.subscribe((event) => {
        if (event.id === 'jenny:open_menu') {
            const player = event.sourceEntity;
            const entity = event.initiator;
            
            if (player && entity) {
                openStateMenu(player, entity);
            }
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
            openStateMenu(player, entity);
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
    
    // Test message
    world.sendMessage('§a[Jenny Mod] Script loaded successfully!');
}

// Initialize on world load
system.runInterval(() => {
    init();
}, 1);
