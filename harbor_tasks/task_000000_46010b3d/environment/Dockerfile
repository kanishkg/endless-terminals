FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    bash \
    coreutils \
    procps \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /opt/ibm/ILOG/CPLEX_Studio221/cplex/bin/x86-64_linux

RUN cat > /opt/ibm/ILOG/CPLEX_Studio221/cplex/bin/x86-64_linux/cplex << 'CPLEXEOF'
#!/usr/bin/env python3
"""
Mock CPLEX binary that simulates memory behavior based on ulimit -v settings.
"""
import os
import sys
import resource

def get_virtual_memory_limit():
    """Get the current virtual memory limit in bytes."""
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    return soft

def main():
    args = sys.argv[1:]

    # Parse -c argument for commands
    commands = []
    i = 0
    while i < len(args):
        if args[i] == '-c':
            i += 1
            while i < len(args):
                commands.append(args[i])
                i += 1
        else:
            i += 1

    lp_file = None
    sol_file = None

    for cmd in commands:
        if cmd.startswith('read '):
            lp_file = cmd.split(' ', 1)[1].strip('"\'')
        elif cmd.startswith('write '):
            sol_file = cmd.split(' ', 1)[1].strip('"\'')

    # Check virtual memory limit
    vlimit = get_virtual_memory_limit()

    # 2GB = 2097152 KB = 2147483648 bytes
    # If limit is set and less than 8GB, simulate out of memory
    too_small_limit = 8 * 1024 * 1024 * 1024  # 8GB threshold

    if lp_file:
        print(f"CPLEX> read {lp_file}")
        if os.path.exists(lp_file):
            print(f"Problem 'dispatch.lp' read.")
            print("Read time = 0.43 sec.")
        else:
            print(f"CPLEX Error: File {lp_file} not found.")
            sys.exit(1)

    # Check for optimize command
    if 'optimize' in commands:
        print("CPLEX> optimize")

        # If virtual memory limit is too restrictive, fail with memory error
        if vlimit != resource.RLIM_INFINITY and vlimit < too_small_limit:
            print("CPXERR_NO_MEMORY: Out of memory.")
            sys.exit(1)

        # Otherwise, simulate successful solve
        print("Tried aggregator 2 times.")
        print("MIP Presolve eliminated 12847 rows and 28934 columns.")
        print("Aggregator did 8234 substitutions.")
        print("Reduced MIP has 29153 rows, 83421 columns, and 412847 nonzeros.")
        print("Reduced MIP has 41234 binaries, 0 generals, 0 SOSs, and 0 indicators.")
        print("Presolve time = 1.23 sec. (847.23 ticks)")
        print("")
        print("Root node processing (before b&c):")
        print("  Real time             =    2.34 sec. (1523.45 ticks)")
        print("Parallel b&c, 4 threads:")
        print("  Real time             =    5.67 sec. (3847.23 ticks)")
        print("  Sync time (average)   =    0.12 sec.")
        print("  Wait time (average)   =    0.03 sec.")
        print("                          ------------")
        print("Total (root+branch&cut) =    8.01 sec. (5370.68 ticks)")
        print("")
        print("Solution pool: 3 solutions saved.")
        print("")
        print("MIP - Integer optimal solution:  Objective =  1.2847234500e+06")
        print("Solution time =    8.01 sec.  Iterations = 48234  Nodes = 127")

    if sol_file:
        print(f"CPLEX> write {sol_file}")
        # Write a valid solution file
        with open(sol_file, 'w') as f:
            f.write('<?xml version = "1.0" encoding="UTF-8" standalone="yes"?>\n')
            f.write('<CPLEXSolution version="1.2">\n')
            f.write(' <header\n')
            f.write('   problemName="dispatch"\n')
            f.write('   solutionName="incumbent"\n')
            f.write('   solutionIndex="-1"\n')
            f.write('   objectiveValue="1284723.45"\n')
            f.write('   solutionTypeValue="3"\n')
            f.write('   solutionTypeString="integer optimal solution"\n')
            f.write('   solutionStatusValue="101"\n')
            f.write('   solutionStatusString="integer optimal solution"\n')
            f.write('   MIPNodes="127"\n')
            f.write('   MIPIterations="48234"\n')
            f.write('   writeLevel="1"/>\n')
            f.write(' <quality\n')
            f.write('   epInt="1e-05"\n')
            f.write('   epRHS="1e-06"\n')
            f.write('   maxIntInfeas="0"\n')
            f.write('   maxPrimalInfeas="0"\n')
            f.write('   maxX="1"\n')
            f.write('   maxSlack="47823.234"/>\n')
            f.write(' <linearConstraints>\n')
            f.write(' </linearConstraints>\n')
            f.write(' <variables>\n')
            for i in range(100):
                f.write(f'  <variable name="x{i}" index="{i}" value="{i % 2}"/>\n')
            f.write(' </variables>\n')
            f.write('</CPLEXSolution>\n')
        print(f"Solution written to file '{sol_file}'.")

    sys.exit(0)

if __name__ == '__main__':
    main()
CPLEXEOF

RUN chmod +x /opt/ibm/ILOG/CPLEX_Studio221/cplex/bin/x86-64_linux/cplex

RUN mkdir -p /home/user/solver/tmp && chmod -R 0777 /home/user/solver

RUN python3 << 'LPGENEOF'
import random
random.seed(42)

num_vars = 120000
num_constraints = 50000

with open('/home/user/solver/dispatch.lp', 'w') as f:
    f.write('\\ Dispatch scheduling MIP model\n')
    f.write('\\ Generated for CPLEX memory testing\n')
    f.write('\n')
    f.write('Minimize\n')
    f.write(' obj: ')

    # Objective function
    terms = []
    for i in range(min(1000, num_vars)):
        coef = random.randint(1, 100)
        terms.append(f'{coef} x{i}')
    f.write(' + '.join(terms[:50]))
    for j in range(50, len(terms), 50):
        f.write('\n      + ' + ' + '.join(terms[j:j+50]))
    f.write('\n\n')

    f.write('Subject To\n')

    # Generate constraints
    for c in range(num_constraints):
        num_terms = random.randint(3, 10)
        var_indices = random.sample(range(num_vars), num_terms)
        terms = []
        for vi in var_indices:
            coef = random.randint(-10, 10)
            if coef == 0:
                coef = 1
            if coef > 0:
                terms.append(f'{coef} x{vi}')
            else:
                terms.append(f'- {-coef} x{vi}')

        rhs = random.randint(1, 100)
        constraint_type = random.choice(['<=', '>=', '='])

        f.write(f' c{c}: ')
        first_term = terms[0]
        if first_term.startswith('- '):
            f.write(first_term)
        else:
            f.write(first_term)
        for t in terms[1:]:
            if t.startswith('- '):
                f.write(f' {t}')
            else:
                f.write(f' + {t}')
        f.write(f' {constraint_type} {rhs}\n')

    f.write('\n')
    f.write('Bounds\n')
    for i in range(num_vars):
        f.write(f' 0 <= x{i} <= 1\n')

    f.write('\n')
    f.write('Binary\n')
    for i in range(0, num_vars, 3):
        f.write(f' x{i}\n')

    f.write('\n')
    f.write('General\n')
    for i in range(1, num_vars, 3):
        f.write(f' x{i}\n')

    f.write('\n')
    f.write('End\n')

print("Generated dispatch.lp")
LPGENEOF

RUN cat > /home/user/solver/run_cplex.sh << 'SCRIPTEOF'
#!/bin/bash
export CPLEX_TMPDIR=/home/user/solver/tmp
ulimit -v 2097152
/opt/ibm/ILOG/CPLEX_Studio221/cplex/bin/x86-64_linux/cplex -c "read /home/user/solver/dispatch.lp" "optimize" "write /home/user/solver/solution.sol"
SCRIPTEOF

RUN chmod +x /home/user/solver/run_cplex.sh

RUN cat > /home/user/solver/cplex.log << 'LOGEOF'
CPLEX> read /home/user/solver/dispatch.lp
Problem 'dispatch.lp' read.
Read time = 0.43 sec.
CPLEX> optimize
CPXERR_NO_MEMORY: Out of memory.
LOGEOF

RUN chmod -R 0777 /home/user

RUN useradd -m -d /home/user -s /bin/bash user || true

RUN chown -R user:user /home/user 2>/dev/null || chmod -R 0777 /home/user

WORKDIR /home/user

USER user

CMD ["/bin/bash"]
