FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    findutils \
    coreutils \
    bash \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/scripts && chmod 0777 /home/user/scripts
RUN mkdir -p /home/user/builds && chmod 0777 /home/user/builds

RUN cat > /home/user/scripts/cleanup.sh << 'EOF'
#!/bin/bash
cd /home/user/builds

find . -name "*.dSYM" -type d -mtime +7 | while read dsym; do
    ipa="${dsym%.dSYM}.ipa"
    if [ ! -e "$ipa" ]; then
        echo "$dsym"
    fi
done | xargs rm -rf
EOF

RUN chmod +x /home/user/scripts/cleanup.sh

RUN mkdir -p "/home/user/builds/MyApp 2.1 (build 447).dSYM/Contents/Resources/DWARF" && \
    echo "binary data placeholder" > "/home/user/builds/MyApp 2.1 (build 447).dSYM/Contents/Resources/DWARF/MyApp"

RUN mkdir -p "/home/user/builds/MyApp 2.2 (build 512).dSYM/Contents/Resources/DWARF" && \
    echo "binary data placeholder" > "/home/user/builds/MyApp 2.2 (build 512).dSYM/Contents/Resources/DWARF/MyApp"

RUN echo "IPA archive placeholder" > "/home/user/builds/MyApp 2.2 (build 512).ipa"

RUN mkdir -p "/home/user/builds/Release-Candidate.dSYM/Contents/Resources/DWARF" && \
    echo "binary data placeholder" > "/home/user/builds/Release-Candidate.dSYM/Contents/Resources/DWARF/Release-Candidate"

RUN mkdir -p "/home/user/builds/Nightly [2024-01-15].dSYM/Contents/Resources/DWARF" && \
    echo "binary data placeholder" > "/home/user/builds/Nightly [2024-01-15].dSYM/Contents/Resources/DWARF/Nightly"

RUN mkdir -p "/home/user/builds/Legacy App-v1.0.dSYM/Contents/Resources/DWARF" && \
    echo "binary data placeholder" > "/home/user/builds/Legacy App-v1.0.dSYM/Contents/Resources/DWARF/Legacy App"

RUN echo "IPA archive placeholder" > "/home/user/builds/Legacy App-v1.0.ipa"

RUN mkdir -p "/home/user/builds/TestFlight (internal).dSYM/Contents/Resources/DWARF" && \
    echo "binary data placeholder" > "/home/user/builds/TestFlight (internal).dSYM/Contents/Resources/DWARF/TestFlight"

RUN touch -d "10 days ago" "/home/user/builds/MyApp 2.1 (build 447).dSYM" && \
    touch -d "10 days ago" "/home/user/builds/MyApp 2.1 (build 447).dSYM/Contents" && \
    touch -d "10 days ago" "/home/user/builds/MyApp 2.1 (build 447).dSYM/Contents/Resources" && \
    touch -d "10 days ago" "/home/user/builds/MyApp 2.1 (build 447).dSYM/Contents/Resources/DWARF" && \
    touch -d "10 days ago" "/home/user/builds/MyApp 2.1 (build 447).dSYM/Contents/Resources/DWARF/MyApp"

RUN touch -d "10 days ago" "/home/user/builds/MyApp 2.2 (build 512).dSYM" && \
    touch -d "10 days ago" "/home/user/builds/MyApp 2.2 (build 512).dSYM/Contents" && \
    touch -d "10 days ago" "/home/user/builds/MyApp 2.2 (build 512).dSYM/Contents/Resources" && \
    touch -d "10 days ago" "/home/user/builds/MyApp 2.2 (build 512).dSYM/Contents/Resources/DWARF" && \
    touch -d "10 days ago" "/home/user/builds/MyApp 2.2 (build 512).dSYM/Contents/Resources/DWARF/MyApp"

RUN touch -d "3 days ago" "/home/user/builds/MyApp 2.2 (build 512).ipa"

RUN touch -d "14 days ago" "/home/user/builds/Release-Candidate.dSYM" && \
    touch -d "14 days ago" "/home/user/builds/Release-Candidate.dSYM/Contents" && \
    touch -d "14 days ago" "/home/user/builds/Release-Candidate.dSYM/Contents/Resources" && \
    touch -d "14 days ago" "/home/user/builds/Release-Candidate.dSYM/Contents/Resources/DWARF" && \
    touch -d "14 days ago" "/home/user/builds/Release-Candidate.dSYM/Contents/Resources/DWARF/Release-Candidate"

RUN touch -d "2 days ago" "/home/user/builds/Nightly [2024-01-15].dSYM" && \
    touch -d "2 days ago" "/home/user/builds/Nightly [2024-01-15].dSYM/Contents" && \
    touch -d "2 days ago" "/home/user/builds/Nightly [2024-01-15].dSYM/Contents/Resources" && \
    touch -d "2 days ago" "/home/user/builds/Nightly [2024-01-15].dSYM/Contents/Resources/DWARF" && \
    touch -d "2 days ago" "/home/user/builds/Nightly [2024-01-15].dSYM/Contents/Resources/DWARF/Nightly"

RUN touch -d "20 days ago" "/home/user/builds/Legacy App-v1.0.dSYM" && \
    touch -d "20 days ago" "/home/user/builds/Legacy App-v1.0.dSYM/Contents" && \
    touch -d "20 days ago" "/home/user/builds/Legacy App-v1.0.dSYM/Contents/Resources" && \
    touch -d "20 days ago" "/home/user/builds/Legacy App-v1.0.dSYM/Contents/Resources/DWARF" && \
    touch -d "20 days ago" "/home/user/builds/Legacy App-v1.0.dSYM/Contents/Resources/DWARF/Legacy App"

RUN touch -d "20 days ago" "/home/user/builds/Legacy App-v1.0.ipa"

RUN touch -d "8 days ago" "/home/user/builds/TestFlight (internal).dSYM" && \
    touch -d "8 days ago" "/home/user/builds/TestFlight (internal).dSYM/Contents" && \
    touch -d "8 days ago" "/home/user/builds/TestFlight (internal).dSYM/Contents/Resources" && \
    touch -d "8 days ago" "/home/user/builds/TestFlight (internal).dSYM/Contents/Resources/DWARF" && \
    touch -d "8 days ago" "/home/user/builds/TestFlight (internal).dSYM/Contents/Resources/DWARF/TestFlight"

RUN chmod -R 0777 /home/user/builds && \
    chmod -R 0777 /home/user/scripts

WORKDIR /home/user

CMD ["/bin/bash"]
