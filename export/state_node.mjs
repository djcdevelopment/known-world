// export/state_node.mjs: buildState under Node (vm sandbox, no browser). Prints exact activity at the given frames as JSON.
//   node export/state_node.mjs --data <kw-data.js> --frames 100,2000,2600
import fs from 'fs';
import path from 'path';
import vm from 'vm';
const A = Object.fromEntries(process.argv.slice(2).reduce((acc, v, i, arr) => { if (v.startsWith('--')) acc.push([v.slice(2), arr[i + 1]]); return acc; }, []));
const root = path.resolve(new URL('..', import.meta.url).pathname);
const ctx = vm.createContext({atob: globalThis.atob});
ctx.window = ctx;
for (const file of [path.resolve(A.data), root + '/render/data.js', root + '/render/state.js']) vm.runInContext(fs.readFileSync(file, 'utf8'), ctx, {filename: file});
const out = {};
for (const f of A.frames.split(',').map(Number)) {
  out[f] = vm.runInContext(`(function(f){const S=KW.newState();KW.buildState(f,S);return Array.from(S.exact);})(${f})`, ctx);
}
console.log(JSON.stringify({node: process.version, R: ctx.KW.D.R, G: ctx.KW.D.G, state: out}));
