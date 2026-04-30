Been trying to run my dataset prep script at /home/user/research/prep_data.py and it's failing with some numpy error about module 'numpy' has no attribute 'float'. Pretty sure this worked last week? I haven't touched the script. Only thing I remember doing recently was updating some packages for another project but I thought I was in a different venv at the time — maybe I wasn't.

    Anyway the script needs to actually run and dump the cleaned parquet to /home/user/research/output/. Don't downgrade numpy if you can avoid it, we need 1.24+ for some other stuff in the lab.
