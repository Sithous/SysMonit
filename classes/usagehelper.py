import psutil, html, os
from datetime import datetime, timedelta

class UsageHelper():
	def __init__(self):
		return

	def bytes2human(self, n):
		"""
		>>> bytes2human(10000)
		'9K'
		>>> bytes2human(100001221)
		'95M'
		"""
		symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
		prefix = {}
		for i, s in enumerate(symbols):
			prefix[s] = 1 << (i + 1) * 10
		for s in reversed(symbols):
			if n >= prefix[s]:
				value = int(float(n) / prefix[s])
				return '%s%s' % (value, s)
		return "%sB" % n

	def running_processes(self):
		procs = []
		procs_status = {}
		for p in psutil.process_iter():
			try:
				p.dict = p.as_dict(['username', 'nice', 'memory_info',
									'memory_percent', 'cpu_percent',
									'cpu_times', 'name', 'status'])
				try:
					procs_status[p.dict['status']] += 1
				except (KeyError):
					procs_status[p.dict['status']] = 1
			except (psutil.NoSuchProcess):
				pass
			else:
				procs.append(p)

		# return processes sorted by CPU percent usage
		processes = sorted(procs, key=lambda p: p.dict['cpu_percent'], reverse=True)
		return (processes, procs_status, psutil.cpu_percent(), psutil.cpu_percent(interval=0, percpu=True), psutil.virtual_memory(), psutil.swap_memory(), os.getloadavg())

	def running_processes_to_html(self, procs, procs_status, cpu_usage, percpu, mem, swap, load_average):
		def get_dashes(perc):
			dashes = "|" * int((float(perc) / 10 * 4))
			empty_dashes = "&nbsp;" * (40 - len(dashes))
			return dashes, empty_dashes

		message = ''
		num_procs = len(procs)

		message += '<hr />'
		message += '<div style="margin-left: 15px; font-family: Monospace;">' # start margin left

		# Show each CPU core and usage
		for cpu_num, perc in enumerate(percpu):
			dashes, empty_dashes = get_dashes(perc)
			message += ("<div> CPU%-2s [%s%s] %5s%% </div>" % (cpu_num, dashes, empty_dashes, perc))

		# Show mem usage
		dashes, empty_dashes = get_dashes(mem.percent)
		message += "<div> Mem&nbsp;&nbsp;[%s%s] %5s%% %6s/%s </div>" % (
			dashes, empty_dashes,
			mem.percent,
			str(int((mem.total - mem.available) / 1024 / 1024)) + "M",
			str(int(mem.total / 1024 / 1024)) + "M"
		)

		# Show swap usage
		dashes, empty_dashes = get_dashes(swap.percent)
		message += "<div> Swap&nbsp;[%s%s] %5s%% %6s/%s </div>" % (
			dashes, empty_dashes,
			swap.percent,
			str(int(swap.used / 1024 / 1024)) + "M",
			str(int(swap.total / 1024 / 1024)) + "M"
		)

		# Show total CPU usage
		message += ("<div> CPU Usage: %s%%</div>" % cpu_usage)

		# Show number of processes
		st = []
		for x, y in procs_status.items():
			if y:
				st.append("%s=%s" % (x, y))
		st.sort(key=lambda x: x[:3] in ('run', 'sle'), reverse=1)
		message += ("<div> Processes: %s (%s)</div>" % (num_procs, ' '.join(st)))

		# Show load average and uptime
		uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
		av1, av2, av3 = load_average
		message += "<div> Load average: %.2f %.2f %.2f  Uptime: %s</div>" \
			% (av1, av2, av3, str(uptime).split('.')[0])

		message += '</div>' # End margin left

		# List out processes
		message += "<hr />"
		message += "<table>"
		message += "<tr> <th>%-6s</th> <th>%-8s</th> <th>%4s</th> <th>%5s</th> <th>%5s</th> <th>%6s</th> <th>%4s</th> <th>%9s</th>  <th>%2s</th> </tr>" % ("PID", "USER", "NI", "VIRT", "RES", "CPU%", "MEM%", "TIME+", "NAME")
		for p in procs:
			# TIME+ column shows process CPU cumulative time and it
			# is expressed as: "mm:ss.ms"
			if p.dict['cpu_times'] is not None:
				ctime = timedelta(seconds=sum(p.dict['cpu_times']))
				ctime = "%s:%s.%s" % (ctime.seconds // 60 % 60,
									  str((ctime.seconds % 60)).zfill(2),
									  str(ctime.microseconds)[:2])
			else:
				ctime = ''

			if p.dict['memory_percent'] is not None:
				p.dict['memory_percent'] = round(p.dict['memory_percent'], 1)
			else:
				p.dict['memory_percent'] = ''

			if p.dict['cpu_percent'] is None:
				p.dict['cpu_percent'] = ''

			if p.dict['username']:
				username = p.dict['username']
			else:
				username = ""

			message += ("<tr> <td>%-6s</td> <td>%-8s</td> <td>%4s</td> <td>%5s</td> <td>%5s</td> <td>%6s</td> <td>%4s</td> <td>%9s</td>  <td>%2s</td> </tr>" % (html.escape(str(p.pid or '')),
							html.escape(str(username or '')),
							html.escape(str(p.dict['nice'])),
							html.escape(str(self.bytes2human(getattr(p.dict['memory_info'], 'vms', 0)))),
							html.escape(str(self.bytes2human(getattr(p.dict['memory_info'], 'rss', 0)))),
							html.escape(str(p.dict['cpu_percent'])),
							html.escape(str(p.dict['memory_percent'])),
							html.escape(str(ctime or '')),
							html.escape(str(p.dict['name'] or '')),
							))
		message += '</table>'
		message += '<hr />'

		return message


