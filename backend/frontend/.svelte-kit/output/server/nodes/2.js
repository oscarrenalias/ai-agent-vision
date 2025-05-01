

export const index = 2;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/_page.svelte.js')).default;
export const imports = ["_app/immutable/nodes/2.C5yTK9vE.js","_app/immutable/chunks/BYDQNPMj.js","_app/immutable/chunks/DGRzr_AR.js"];
export const stylesheets = ["_app/immutable/assets/2.DwB_n-T4.css"];
export const fonts = [];
