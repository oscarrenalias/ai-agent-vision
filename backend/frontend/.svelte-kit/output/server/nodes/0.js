import * as universal from '../entries/pages/_layout.js';

export const index = 0;
let component_cache;
export const component = async () => component_cache ??= (await import('../entries/pages/_layout.svelte.js')).default;
export { universal };
export const universal_id = "src/routes/+layout.js";
export const imports = ["_app/immutable/nodes/0.Cf-wI0Aw.js","_app/immutable/chunks/BYDQNPMj.js","_app/immutable/chunks/DGRzr_AR.js","_app/immutable/chunks/C4B192fd.js","_app/immutable/chunks/BhXfAO3M.js","_app/immutable/chunks/CoQb8LEH.js"];
export const stylesheets = ["_app/immutable/assets/ChatWindow.CnOLRhNV.css","_app/immutable/assets/0.DY6b7RpQ.css"];
export const fonts = [];
