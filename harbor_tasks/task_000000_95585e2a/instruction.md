I'm setting up a monitoring infrastructure and need to add an external alerting library as a git submodule to my project.

I have an existing git repository at `/home/user/monitoring-project`. I need you to add the prometheus alertmanager repository (https://github.com/prometheus/alertmanager.git) as a submodule in the `external/alertmanager` directory within my project.

After adding the submodule, please create a verification log file at `/home/user/monitoring-project/submodule-setup.log` that contains the following information in this exact format:

```
SUBMODULE_PATH: external/alertmanager
SUBMODULE_URL: <the actual URL of the submodule>
SUBMODULE_STATUS: <output of git submodule status for this submodule>
SETUP_COMPLETE: true
```

Each line should start exactly with the label shown (like `SUBMODULE_PATH:`) followed by a space and then the value. The `SUBMODULE_URL` should be extracted from the git configuration, and `SUBMODULE_STATUS` should show the commit hash and path as reported by git.

Make sure the submodule is properly initialized and the `.gitmodules` file is created in the repository root.
