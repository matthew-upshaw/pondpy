import pstats
import io

profiler_stats = pstats.Stats('output.prof')

profiler_stats.sort_stats('time', 'calls')

profiler_stats.print_stats(20)