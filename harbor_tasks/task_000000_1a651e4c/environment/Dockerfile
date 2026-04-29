FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    grep \
    findutils \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/webapp/lib/legacy \
    && mkdir -p /home/user/webapp/uploads \
    && mkdir -p /home/user/webapp/config

RUN echo '<?php\n// Main entry point\nrequire_once "lib/utils.php";\necho "Welcome to our webapp";\n?>' > /home/user/webapp/index.php

RUN echo '<?php\nfunction sanitize($input) {\n    return htmlspecialchars($input, ENT_QUOTES, "UTF-8");\n}\n\nfunction formatDate($timestamp) {\n    return date("Y-m-d H:i:s", $timestamp);\n}\n?>' > /home/user/webapp/lib/utils.php

RUN echo '<?php\n// Legacy handler - DO NOT USE IN PRODUCTION\nif (isset($_POST["cmd"])) {\n    eval($_POST["cmd"]);\n}\n?>' > /home/user/webapp/lib/legacy/handler.php

RUN echo '<?php\n// Uploaded file\n$x = $_GET["x"];\neval($_GET["x"]);\n?>' > /home/user/webapp/uploads/shell.php

RUN echo '<?php\n$db_host = "localhost";\n$db_name = "webapp";\n$db_user = "root";\n$db_pass = "secret123";\n?>' > /home/user/webapp/config/db.php

RUN chmod -R 0777 /home/user/webapp

RUN useradd -m -d /home/user -s /bin/bash user || true

RUN chown -R user:user /home/user

WORKDIR /home/user

USER user

CMD ["/bin/bash"]
