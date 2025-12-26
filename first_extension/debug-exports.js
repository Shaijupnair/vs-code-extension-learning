try {
    const plugin = require('@orama/plugin-data-persistence');
    console.log('✅ Success: @orama/plugin-data-persistence loaded.');
    console.log('--- EXPORTS ---');
    console.log(plugin);

    // Check for expected functions if known, e.g., persist, restore
    if (plugin.persist) console.log('Found export: persist');
    if (plugin.restore) console.log('Found export: restore');

} catch (e) {
    console.error('❌ Error: Could not load plugin.');
    console.error(e);
}
