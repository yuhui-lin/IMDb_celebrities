// rollup.config.js
import resolve from 'rollup-plugin-node-resolve';
import typescript from 'rollup-plugin-typescript2';

export default {
    input: 'main.ts',
    output: {
        file: 'bundle.js',
        format: 'umd',
        // when using export, output.name is necessary! otherwise:
        // Error: You must supply options.name for UMD bundles
        name: 'bundle'
    },
    plugins: [
        resolve(),
        typescript()
    ]
};