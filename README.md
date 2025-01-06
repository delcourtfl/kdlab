

### First step

Inital simple program :
Key press -> Windows/Linux App -> Display key pressed

Better to create a generic testbench to compare results

2 Parts :
    - Press/Display
    - Latency measurement

Script 2 : 
Simulate key press the same way to all,
Store start timestamp,
Detect display modification,
Store last timestamp,
Compare both

Should I run them in // ? Could they interfere with each others ? Won't it impact performances if there is no warmup

### Automation

### Optimise

## Program
## Language
## Driver
## OS
## Hardware ?
## Isolated Env ?
## Screen Refresh Rate ?

https://github.com/msaroufim/awesome-profiling

### How to Debug
# Slower CPU + GPU
# More inputs and get average

What I trie to benchmark
- Windows Hooks
- Windows Performance Recordre / Analyzer
- cProfile
- Timeit
- Python ETW Trace ?

### Related Work :

https://github.com/pavelfatin/typometer