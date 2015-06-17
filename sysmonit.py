import configparser, psutil, time, sys, smtplib, os
from classes.scheduler import PeriodicExecutor
from classes.usagehelper import UsageHelper
from classes.emailhelper import EmailHelper

# psutil.cpu_percent()

class SystemMonitor():
	"Monitor system usage"
	def __init__(self):
		self.config = configparser.SafeConfigParser()
		self.config.read('config.ini')
		self.debug = self.config.get('config', 'debug')
		self.usageHelper = UsageHelper()
		self.emailHelper = EmailHelper(self.config)

		# internal options -- do not change
		self.cpu_usage_trigger = False 

	def check_cpu_usage(self):
		procs = self.usageHelper.running_processes()
		current_cpu_usage = procs[2]
		if (current_cpu_usage > self.config.getfloat('cpu_monitor', 'notify_percentage')):
			if (self.debug):
				print("CPU usage over limit (", current_cpu_usage, "% > ", self.config.getfloat('cpu_monitor', 'notify_percentage'), ")")
			if not self.cpu_usage_trigger:
				self.cpu_usage_trigger = True
				if (self.debug):
					print("Sending email about CPU usage...")
				self.emailHelper.sendMail(self.config.get('config', 'pcname') + ': CPU usage high', self.emailHelper.dialogBox('alert', 'CPU usage of '+str(current_cpu_usage)+'% matches resource limit [cpu usage > '+self.config.get('cpu_monitor', 'notify_percentage')+']') + self.usageHelper.running_processes_to_html(*procs))
		else:
			if (self.debug):
				print("CPU usage okay (", current_cpu_usage, "% < ", self.config.get('cpu_monitor', 'notify_percentage'), ")")
			if self.cpu_usage_trigger:
				self.cpu_usage_trigger = False
				if (self.debug):
					print("Sending email that CPU limit is OK..")
				self.emailHelper.sendMail(self.config.get('config', 'pcname') + ': CPU ok', self.emailHelper.dialogBox('success', 'CPU usage has gone back to reasonable limits.') + self.usageHelper.running_processes_to_html(*procs))


try:
	monitor = SystemMonitor()

	# Start periodic tasks
	check_cpu_task = PeriodicExecutor(monitor.config.getfloat('cpu_monitor', 'interval'), monitor.check_cpu_usage, [])
	check_cpu_task.start()

	# prevent window from closing so periodic threads tasks running
	# There is probably a better way of doing this..
	while True:
		time.sleep(1)
except (KeyboardInterrupt):
	print("Shutting down..")
	sys.exit()