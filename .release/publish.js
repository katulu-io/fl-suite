const semanticRelease = require("semantic-release");

(async () => {
  try {
    const result = await semanticRelease(
      {
        extends: "./release.config.js",
        plugins: ["@semantic-release/commit-analyzer", "@semantic-release/release-notes-generator"],
        prepare: [
          { path: "./.release/src/kustomize.js", dir: "./kustomize/fl-suite/overlays/standalone", out: "./dist/fl-suite-${nextRelease.version}.tgz" },
          { path: "./.release/src/kustomize.js", dir: "./kustomize/fl-edge/base", out: "./dist/fl-edge-${nextRelease.version}.tgz" },
        ],
        publish: [
          {
            path: "@semantic-release/github",
            assets: [{ path: "dist/*.tgz" }],
          },
        ],
        ci: false,
      },
      {
        cwd: "../",
      }
    );

    if (result) {
      const { commits, nextRelease } = result;

      console.log(
        `Published ${nextRelease.type} release version ${nextRelease.version} containing ${commits.length} commits.`
      );
    } else {
      console.log("No release published.");
    }

    // Get stdout and stderr content
  } catch (err) {
    console.error("The automated release failed with %O", err);
    process.exit(1);
  }
})();
