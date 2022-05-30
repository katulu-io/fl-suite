const semanticRelease = require("semantic-release");
var stream = require("stream");

class Mute extends stream.Writable {
  _write(chunk, encoding, callback) {}
}

(async () => {
  try {
    const result = await semanticRelease(
      {
        extends: "./release.config.js",
        dryRun: true,
        plugins: ["@semantic-release/commit-analyzer"],
      },
      {
        cwd: "../",
        stdout: new Mute(),
      }
    );
    if (result) {
      const { nextRelease } = result;
      process.stdout.write(`MAKEVAR_VERSION=${nextRelease.version}`);
    } else {
      console.error("Version couldn't be determined.");
    }
  } catch (err) {
    console.error("Release `env` creation failed with %O", err);
    process.exit(1);
  }
})();
