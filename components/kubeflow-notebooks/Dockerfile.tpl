FROM public.ecr.aws/j1r0q0g6/notebooks/notebook-servers/jupyter-pytorch-full:v1.5.0

LABEL org.opencontainers.image.source https://github.com/katulu-io/fl-suite

COPY --chown=jovyan:users \
  fl_suite-$$container-tag$$-py3-none-any.whl \
  requirements.txt \
  /tmp/
RUN python3 -m pip install -r /tmp/requirements.txt --quiet --no-cache-dir \
  && rm -f /tmp/requirements.txt && rm -f /tmp/*.whl
