// console.log(__dirname);
// console.log(process.cwd());

// Load file from disk
const fs = require("fs");
const path = require("path");
const yaml = require("js-yaml");
const tar = require("tar");
const template = require("lodash.template");

const KUSTOMIZE_FILENAMES = ["kustomization.yaml", "kustomization.yml"];

const isFile = (filePath) => fs.existsSync(filePath) && fs.statSync(filePath).isFile();

const isKustomizeFile = (filePath) => {
  if (typeof filePath !== "string") {
    return false;
  }

  return KUSTOMIZE_FILENAMES.some((fileName) => filePath.endsWith(fileName)) && isFile(filePath);
};

const getResourcePath = (kustomizeFilePath, filePath) =>
  path.join(path.dirname(kustomizeFilePath), filePath.replace(/^.*=/, ""));
exports.getResourcePath = getResourcePath;

const getKustomizePath = (basePath) =>
  [basePath, ...KUSTOMIZE_FILENAMES.map((fileName) => path.join(basePath, fileName))].find(isKustomizeFile);

const loadKustomize = (filePath) => {
  if (typeof filePath !== "string") {
    return [];
  }

  const file = fs.readFileSync(filePath, "utf-8");

  try {
    return yaml.loadAll(file).map((content) => ({
      filePath,
      content,
    }));
  } catch (e) {
    console.error('Error parsing "%s"', filePath);
    return [];
  }
};

const getKustomizeResources = ({ filePath, content }) => {
  if (content == null) {
    return [];
  }

  return [...(content.bases || []), ...(content.resources || [])].map((resource) =>
    getResourcePath(filePath, resource)
  );
};
exports.getKustomizeResources = getKustomizeResources;

const getCRDResources = ({ filePath, content }) => {
  if (content == null || content.crds == null) {
    return [];
  }

  return content.crds.map((resource) => getResourcePath(filePath, resource));
};
exports.getCRDResources = getCRDResources;

const getConfigMapGeneratorResources = ({ filePath, content }) => {
  if (content == null || content.configMapGenerator == null) {
    return [];
  }
  return content.configMapGenerator
    .flatMap(({ files, envs }) => [...(files || []), ...(envs || [])])
    .map((config) => {
      return getResourcePath(filePath, config);
    });
};
exports.getConfigMapGeneratorResources = getConfigMapGeneratorResources;

const getConfigurationResources = ({ filePath, content }) => {
  if (content == null || content.configurations == null) {
    return [];
  }
  return content.configurations.map((config) => {
    return getResourcePath(filePath, config);
  });
};
exports.getConfigurationResources = getConfigurationResources;

const getOpenAPISchemaResources = ({ filePath, content }) => {
  if (content == null || content.openapi == null || content.openapi.path == null) {
    return [];
  }

  return [getResourcePath(filePath, content.openapi.path)];
};
exports.getOpenAPISchemaResources = getOpenAPISchemaResources;

const getPatchResources = ({ filePath, content }) => {
  if (content == null || content.patches == null) {
    return [];
  }
  return content.patches.filter(({ path }) => path != null).map((patch) => getResourcePath(filePath, patch.path));
};
exports.getPatchResources = getPatchResources;

const getJson6902PatchResources = ({ filePath, content }) => {
  if (content == null || content.patchesJson6902 == null) {
    return [];
  }

  return content.patchesJson6902
    .filter(({ path }) => path != null)
    .map((patch) => getResourcePath(filePath, patch.path));
};
exports.getJson6902PatchResources = getJson6902PatchResources;

const getStrategicMergeResources = ({ filePath, content }) => {
  if (content == null || content.patchesStrategicMerge == null) {
    return [];
  }
  return content.patchesStrategicMerge.map((patch) => getResourcePath(filePath, patch));
};
exports.getStrategicMergeResources = getStrategicMergeResources;

const getReplacementResources = ({ filePath, content }) => {
  if (content == null || content.replacements == null) {
    return [];
  }
  return content.replacements.map((replacement) => getResourcePath(filePath, replacement.path));
};
exports.getReplacementResources = getReplacementResources;

const getSecretGeneratorResources = ({ filePath, content }) => {
  if (content == null || content.secretGenerator == null) {
    return [];
  }
  return content.secretGenerator
    .flatMap(({ files, envs }) => [...(files || []), ...(envs || [])])
    .map((config) => {
      return getResourcePath(filePath, config);
    });
};
exports.getSecretGeneratorResources = getSecretGeneratorResources;

const getAllResources = (kustomizePath) =>
  loadKustomize(kustomizePath).flatMap((file) => [
    file.filePath,
    ...getConfigMapGeneratorResources(file),
    ...getConfigurationResources(file),
    ...getCRDResources(file),
    ...getOpenAPISchemaResources(file),
    ...getPatchResources(file),
    ...getJson6902PatchResources(file),
    ...getStrategicMergeResources(file),
    ...getReplacementResources(file),
    ...getSecretGeneratorResources(file),
    ...getKustomizeResources(file).flatMap((resource) => {
      const kustomizePath = getKustomizePath(resource);

      // if the resource is a kustomization file, recursively load it
      if (kustomizePath != null) {
        return getAllResources(kustomizePath);
      }

      return [resource];
    }),
  ]);

async function prepare(
  { dir, out = "./dist/${nextRelease.version}.tgz", gzip = true },
  { cwd, env, stdout, stderr, logger, ...context }
) {
  const filePath = getKustomizePath(path.join(path.resolve(cwd, dir)));

  if (filePath == null) {
    throw new Error(`No kustomize.yaml found in ${path.join(path.resolve(cwd, dir))}.`);
  }

  // Get output file path
  const outputFilePath = path.resolve(cwd, template(out)(context));

  // create output dir if it doesn't exist
  fs.mkdirSync(path.dirname(outputFilePath), { recursive: true });

  return tar.c(
    {
      file: outputFilePath,
      gzip,
      cwd,
    },
    getAllResources(filePath)
  );
}
exports.prepare = prepare;
