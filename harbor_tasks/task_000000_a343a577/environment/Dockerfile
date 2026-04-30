FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    findutils \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/project/src/utils/helpers \
    && mkdir -p /home/user/project/src/cache \
    && mkdir -p /home/user/project/data/raw/processed \
    && mkdir -p /home/user/project/data/exports \
    && mkdir -p /home/user/project/build/artifacts/temp \
    && mkdir -p /home/user/project/logs/archive \
    && mkdir -p /home/user/project/config \
    && mkdir -p /home/user/project/tests/fixtures/data

RUN echo "print('hello')" > /home/user/project/src/main.py \
    && echo "# utils" > /home/user/project/src/utils/helpers.py \
    && echo '{"name": "project"}' > /home/user/project/config/settings.json \
    && echo "README content" > /home/user/project/README.txt \
    && echo "test data" > /home/user/project/data/sample.csv \
    && echo "log entry" > /home/user/project/logs/app.log \
    && echo "fixture data" > /home/user/project/tests/fixtures/test_data.json \
    && echo "build script" > /home/user/project/build/build.sh

RUN echo "tmp1" > /home/user/project/cache_001.tmp \
    && echo "tmp2" > /home/user/project/cache_002.tmp \
    && echo "tmp3" > /home/user/project/temp_data.tmp \
    && echo "tmp4" > /home/user/project/session.tmp \
    && echo "tmp5" > /home/user/project/upload.tmp

RUN echo "tmp6" > /home/user/project/src/cache_001.tmp \
    && echo "tmp7" > /home/user/project/src/cache_002.tmp \
    && echo "tmp8" > /home/user/project/src/temp_data.tmp \
    && echo "tmp9" > /home/user/project/src/session_abc.tmp \
    && echo "tmp10" > /home/user/project/src/build_artifact.tmp

RUN echo "tmp11" > /home/user/project/src/utils/temp_001.tmp \
    && echo "tmp12" > /home/user/project/src/utils/temp_002.tmp \
    && echo "tmp13" > /home/user/project/src/utils/cache.tmp \
    && echo "tmp14" > /home/user/project/src/utils/session.tmp \
    && echo "tmp15" > /home/user/project/src/utils/data.tmp

RUN echo "tmp16" > /home/user/project/src/utils/helpers/helper_cache.tmp \
    && echo "tmp17" > /home/user/project/src/utils/helpers/temp_file.tmp \
    && echo "tmp18" > /home/user/project/src/utils/helpers/session_data.tmp \
    && echo "tmp19" > /home/user/project/src/utils/helpers/export.tmp \
    && echo "tmp20" > /home/user/project/src/utils/helpers/build.tmp

RUN echo "tmp21" > /home/user/project/src/cache/cache_001.tmp \
    && echo "tmp22" > /home/user/project/src/cache/cache_002.tmp \
    && echo "tmp23" > /home/user/project/src/cache/cache_003.tmp \
    && echo "tmp24" > /home/user/project/src/cache/session.tmp \
    && echo "tmp25" > /home/user/project/src/cache/temp.tmp

RUN echo "tmp26" > /home/user/project/data/export.tmp \
    && echo "tmp27" > /home/user/project/data/import.tmp \
    && echo "tmp28" > /home/user/project/data/cache.tmp \
    && echo "tmp29" > /home/user/project/data/session.tmp \
    && echo "tmp30" > /home/user/project/data/temp_data.tmp

RUN echo "tmp31" > /home/user/project/data/raw/raw_001.tmp \
    && echo "tmp32" > /home/user/project/data/raw/raw_002.tmp \
    && echo "tmp33" > /home/user/project/data/raw/export.tmp \
    && echo "tmp34" > /home/user/project/data/raw/cache.tmp \
    && echo "tmp35" > /home/user/project/data/raw/temp.tmp

RUN echo "tmp36" > /home/user/project/data/raw/processed/proc_001.tmp \
    && echo "tmp37" > /home/user/project/data/raw/processed/proc_002.tmp \
    && echo "tmp38" > /home/user/project/data/raw/processed/cache.tmp \
    && echo "tmp39" > /home/user/project/data/raw/processed/session.tmp \
    && echo "tmp40" > /home/user/project/data/raw/processed/temp.tmp

RUN echo "tmp41" > /home/user/project/build/artifact.tmp \
    && echo "tmp42" > /home/user/project/build/cache.tmp \
    && echo "tmp43" > /home/user/project/build/session.tmp

RUN echo "tmp44" > /home/user/project/build/artifacts/art_001.tmp \
    && echo "tmp45" > /home/user/project/build/artifacts/art_002.tmp \
    && echo "tmp46" > /home/user/project/build/artifacts/cache.tmp

RUN echo "tmp47" > /home/user/project/build/artifacts/temp/temp_001.tmp \
    && echo "tmp48" > /home/user/project/build/artifacts/temp/temp_002.tmp \
    && echo "tmp49" > /home/user/project/build/artifacts/temp/cache.tmp \
    && echo "tmp50" > /home/user/project/build/artifacts/temp/session.tmp

RUN chmod -R 0777 /home/user/project

WORKDIR /home/user

CMD ["/bin/bash"]
