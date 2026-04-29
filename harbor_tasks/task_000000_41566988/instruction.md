Support ticket came in — customer's running `make collect` in /home/user/diagnostics and it's dying partway through. They get partial output in /home/user/diagnostics/out/report.txt but it's missing sections. I tried it myself and yeah, something's choking. The Makefile's supposed to pull info from a few different sources, run some parsers, stitch everything into one report. Been working fine for months so idk what changed.

Need the full report generating — all sections present, no errors on `make collect`.
