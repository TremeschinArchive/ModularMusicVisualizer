import pstats

stats = pstats.Stats("res.prof")

stats.strip_dirs()
stats.sort_stats("tottime")
stats.print_stats(30)

# function_name = "tobytes"
# stats.print_callers('\({}'.format(function_name))
