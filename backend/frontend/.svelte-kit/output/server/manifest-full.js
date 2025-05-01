export const manifest = (() => {
function __memo(fn) {
	let value;
	return () => value ??= (value = fn());
}

return {
	appDir: "_app",
	appPath: "_app",
	assets: new Set(["favicon.png"]),
	mimeTypes: {".png":"image/png"},
	_: {
		client: {start:"_app/immutable/entry/start.Cc6CqXeZ.js",app:"_app/immutable/entry/app.B9Z17M-C.js",imports:["_app/immutable/entry/start.Cc6CqXeZ.js","_app/immutable/chunks/CHs1yHqw.js","_app/immutable/chunks/BYDQNPMj.js","_app/immutable/chunks/CoQb8LEH.js","_app/immutable/entry/app.B9Z17M-C.js","_app/immutable/chunks/BYDQNPMj.js","_app/immutable/chunks/DGRzr_AR.js"],stylesheets:[],fonts:[],uses_env_dynamic_public:false},
		nodes: [
			__memo(() => import('./nodes/0.js')),
			__memo(() => import('./nodes/1.js')),
			__memo(() => import('./nodes/2.js')),
			__memo(() => import('./nodes/3.js')),
			__memo(() => import('./nodes/4.js'))
		],
		routes: [
			{
				id: "/",
				pattern: /^\/$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 2 },
				endpoint: null
			},
			{
				id: "/receipts",
				pattern: /^\/receipts\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 3 },
				endpoint: null
			},
			{
				id: "/receipts/history",
				pattern: /^\/receipts\/history\/?$/,
				params: [],
				page: { layouts: [0,], errors: [1,], leaf: 4 },
				endpoint: null
			}
		],
		prerendered_routes: new Set([]),
		matchers: async () => {

			return {  };
		},
		server_assets: {}
	}
}
})();
