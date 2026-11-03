console.log = console.info = console.debug = (...values) => console.error(...values);
import("./document-parser.mjs").catch(() => { process.stderr.write("Document parser failed to load\n"); process.exitCode = 1; });
