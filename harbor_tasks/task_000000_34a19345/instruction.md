I'm a data analyst and I need help setting up a project that uses shared data processing utilities from another repository.

Here's what I need you to do:

1. Initialize a new git repository at `/home/user/sales_analysis` for my sales data analysis project.

2. Add a git submodule from the repository at `/home/user/shared_utils` (which already exists on my system) into a directory called `utils` within my project.

3. Create an initial commit in my main project that includes the submodule. Use the commit message "Add shared utilities submodule".

4. After completing the setup, create a log file at `/home/user/sales_analysis/setup_log.txt` that contains exactly 3 lines in this format:
   - Line 1: The output of `git submodule status` (run from the project root)
   - Line 2: The word "SUBMODULE_PATH:" followed by a space and then the path shown in `.gitmodules` for the submodule
   - Line 3: The word "SUBMODULE_URL:" followed by a space and then the URL shown in `.gitmodules` for the submodule

The shared_utils repository contains CSV processing scripts that I'll be using across multiple analysis projects, which is why I want it as a submodule rather than copying the files directly.
