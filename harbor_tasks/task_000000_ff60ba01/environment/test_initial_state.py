# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
attempts to fix the ETL dashboard issue.
"""

import os
import subprocess
import json
import pytest


HOME = "/home/user"
ETL_MONITOR = f"{HOME}/etl-monitor"


class TestNodeEnvironment:
    """Verify Node.js and npm are available."""

    def test_node_available(self):
        """Node.js should be installed and accessible."""
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Node.js is not installed or not in PATH"
        # Check for Node 18.x
        version = result.stdout.strip()
        assert version.startswith("v18"), f"Expected Node 18.x, got {version}"

    def test_npm_available(self):
        """npm should be installed and accessible."""
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "npm is not installed or not in PATH"


class TestETLMonitorDirectoryStructure:
    """Verify the ETL monitor directory and its structure exist."""

    def test_etl_monitor_directory_exists(self):
        """The /home/user/etl-monitor directory should exist."""
        assert os.path.isdir(ETL_MONITOR), f"Directory {ETL_MONITOR} does not exist"

    def test_etl_monitor_is_writable(self):
        """The /home/user/etl-monitor directory should be writable."""
        assert os.access(ETL_MONITOR, os.W_OK), f"Directory {ETL_MONITOR} is not writable"

    def test_package_json_exists(self):
        """package.json should exist in the project root."""
        package_json = f"{ETL_MONITOR}/package.json"
        assert os.path.isfile(package_json), f"{package_json} does not exist"

    def test_package_json_has_start_script(self):
        """package.json should have a start script that runs node server.js."""
        package_json = f"{ETL_MONITOR}/package.json"
        with open(package_json, 'r') as f:
            data = json.load(f)
        assert "scripts" in data, "package.json missing 'scripts' section"
        assert "start" in data["scripts"], "package.json missing 'start' script"
        assert "node server.js" in data["scripts"]["start"], \
            "start script should run 'node server.js'"

    def test_package_json_has_express_dependency(self):
        """package.json should have express as a dependency."""
        package_json = f"{ETL_MONITOR}/package.json"
        with open(package_json, 'r') as f:
            data = json.load(f)
        assert "dependencies" in data, "package.json missing 'dependencies' section"
        assert "express" in data["dependencies"], "express not in dependencies"

    def test_server_js_exists(self):
        """server.js should exist in the project root."""
        server_js = f"{ETL_MONITOR}/server.js"
        assert os.path.isfile(server_js), f"{server_js} does not exist"

    def test_server_js_requires_config(self):
        """server.js should require ./config/settings.js."""
        server_js = f"{ETL_MONITOR}/server.js"
        with open(server_js, 'r') as f:
            content = f.read()
        assert "config/settings" in content or "config/settings.js" in content, \
            "server.js should require ./config/settings.js"

    def test_config_directory_exists(self):
        """config directory should exist."""
        config_dir = f"{ETL_MONITOR}/config"
        assert os.path.isdir(config_dir), f"{config_dir} directory does not exist"

    def test_settings_js_exists(self):
        """config/settings.js should exist."""
        settings_js = f"{ETL_MONITOR}/config/settings.js"
        assert os.path.isfile(settings_js), f"{settings_js} does not exist"

    def test_settings_js_uses_js_yaml(self):
        """config/settings.js should use js-yaml to parse app.yaml."""
        settings_js = f"{ETL_MONITOR}/config/settings.js"
        with open(settings_js, 'r') as f:
            content = f.read()
        assert "js-yaml" in content or "yaml" in content, \
            "settings.js should use js-yaml"
        assert "app.yaml" in content, \
            "settings.js should read from app.yaml"

    def test_app_yaml_exists(self):
        """config/app.yaml should exist."""
        app_yaml = f"{ETL_MONITOR}/config/app.yaml"
        assert os.path.isfile(app_yaml), f"{app_yaml} does not exist"

    def test_app_yaml_contains_tab_character(self):
        """config/app.yaml should contain a tab character (the bug)."""
        app_yaml = f"{ETL_MONITOR}/config/app.yaml"
        with open(app_yaml, 'rb') as f:
            content = f.read()
        assert b'\t' in content, \
            "config/app.yaml should contain a tab character (this is the YAML syntax bug)"

    def test_routes_directory_exists(self):
        """routes directory should exist."""
        routes_dir = f"{ETL_MONITOR}/routes"
        assert os.path.isdir(routes_dir), f"{routes_dir} directory does not exist"

    def test_status_route_exists(self):
        """routes/status.js should exist."""
        status_js = f"{ETL_MONITOR}/routes/status.js"
        assert os.path.isfile(status_js), f"{status_js} does not exist"

    def test_status_route_has_status_endpoint(self):
        """routes/status.js should have a /status endpoint."""
        status_js = f"{ETL_MONITOR}/routes/status.js"
        with open(status_js, 'r') as f:
            content = f.read()
        assert "status" in content.lower(), \
            "routes/status.js should define a status endpoint"

    def test_node_modules_exists(self):
        """node_modules directory should exist (dependencies installed)."""
        node_modules = f"{ETL_MONITOR}/node_modules"
        assert os.path.isdir(node_modules), \
            f"{node_modules} does not exist - dependencies not installed"

    def test_express_installed(self):
        """express should be installed in node_modules."""
        express_dir = f"{ETL_MONITOR}/node_modules/express"
        assert os.path.isdir(express_dir), \
            "express is not installed in node_modules"

    def test_js_yaml_installed(self):
        """js-yaml should be installed in node_modules."""
        js_yaml_dir = f"{ETL_MONITOR}/node_modules/js-yaml"
        assert os.path.isdir(js_yaml_dir), \
            "js-yaml is not installed in node_modules"


class TestBashrcConfiguration:
    """Verify the .bashrc has the problematic PORT setting."""

    def test_bashrc_exists(self):
        """.bashrc should exist in home directory."""
        bashrc = f"{HOME}/.bashrc"
        assert os.path.isfile(bashrc), f"{bashrc} does not exist"

    def test_bashrc_is_writable(self):
        """.bashrc should be writable."""
        bashrc = f"{HOME}/.bashrc"
        assert os.access(bashrc, os.W_OK), f"{bashrc} is not writable"

    def test_bashrc_has_invalid_port(self):
        """.bashrc should contain the invalid PORT=65540 setting."""
        bashrc = f"{HOME}/.bashrc"
        with open(bashrc, 'r') as f:
            content = f.read()
        assert "PORT=65540" in content or "PORT = 65540" in content, \
            ".bashrc should contain 'export PORT=65540' (the security hardening bug)"

    def test_bashrc_exports_port(self):
        """.bashrc should export the PORT variable."""
        bashrc = f"{HOME}/.bashrc"
        with open(bashrc, 'r') as f:
            content = f.read()
        assert "export" in content and "PORT" in content, \
            ".bashrc should export the PORT environment variable"


class TestAppYamlContent:
    """Verify app.yaml has the expected structure with the bug."""

    def test_app_yaml_mentions_port_3000(self):
        """app.yaml should specify port 3000 as the desired port."""
        app_yaml = f"{ETL_MONITOR}/config/app.yaml"
        with open(app_yaml, 'r') as f:
            content = f.read()
        assert "3000" in content, \
            "app.yaml should specify port 3000 as the server port"

    def test_app_yaml_has_server_section(self):
        """app.yaml should have a server configuration section."""
        app_yaml = f"{ETL_MONITOR}/config/app.yaml"
        with open(app_yaml, 'r') as f:
            content = f.read()
        assert "server" in content.lower(), \
            "app.yaml should have a server configuration section"

    def test_app_yaml_is_invalid_yaml(self):
        """app.yaml should fail to parse due to tab character."""
        app_yaml = f"{ETL_MONITOR}/config/app.yaml"
        result = subprocess.run(
            ["python3", "-c", f"import yaml; yaml.safe_load(open('{app_yaml}'))"],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0, \
            "app.yaml should fail to parse (contains tab character bug)"


class TestSettingsJsErrorHandling:
    """Verify settings.js has poor error handling (part of the bug)."""

    def test_settings_js_catches_errors(self):
        """settings.js should have a try-catch that swallows errors."""
        settings_js = f"{ETL_MONITOR}/config/settings.js"
        with open(settings_js, 'r') as f:
            content = f.read()
        assert "try" in content and "catch" in content, \
            "settings.js should have try-catch error handling"
        # Check for poor error handling - just logs a warning
        assert "Config warning" in content or "config = {}" in content or "config={}" in content, \
            "settings.js should have poor error handling that swallows the real error"
