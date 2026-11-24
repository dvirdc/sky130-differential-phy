FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends netgen-lvs ngspice build-essential tcl-dev tk-dev libx11-dev libcairo2-dev libglu1-mesa-dev libncurses-dev m4 csh iverilog yosys python3 python3-venv git ca-certificates make && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /opt/eda-venv && /opt/eda-venv/bin/pip install --no-cache-dir ciel==3.2.0 klayout==0.30.8 pyyaml==6.0.2
ENV PATH="/opt/eda-venv/bin:${PATH}"
ARG MAGIC_COMMIT=1d42dfcdf6cd91df7a59198477324c2ca78ba439
RUN git clone https://github.com/RTimothyEdwards/magic.git /tmp/magic && cd /tmp/magic && git checkout "$MAGIC_COMMIT" && ./configure --with-tcl=/usr/lib --with-tk=/usr/lib --disable-opengl && make -j4 && make install && rm -rf /tmp/magic
ENV PDK_ROOT=/pdk
WORKDIR /work
