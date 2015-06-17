from email.mime.text import MIMEText
from smtplib import SMTP_SSL
from smtplib import SMTP

class EmailHelper():
	def __init__(self, config):
		self.config = config
		return

	def dialogBox(self, type, message):
		default_css = 'margin: 15px 0 15px 15px; padding: 15px;'
		css = {
			'alert':   'background-color: rgb(242, 222, 222);',
			'warning': 'background-color: rgb(252, 248, 227);',
			'info':    'background-color: rgb(217, 237, 247);',
			'success': 'background-color: rgb(223, 240, 216);'
		}.get(type, 'background-color: rgb(51, 122, 183);')

		return "<div style=\"" + default_css + css + "\">" + message + "</div>"

	def sendMail(self, subject, message):
		try:
			styles = """
				<style>
					 p{font-family:Arial,Helvetica,sans-serif}
					 p b{color:#07a}
					 hr{border-style:dashed;border-width:1px 0 0 0;border-color:lightgray}
					 small{color:#d3d3d3;font-size:xx-small;font-weight:normal;font-family:Arial,Helvetica,sans-serif}
					 table a:link{color:#666;font-weight:bold;text-decoration:none}
					 table a:visited{color:#999;font-weight:bold;text-decoration:none}
					 table a:active,table a:hover{color:#bd5a35;text-decoration:underline}
					 table{font-family:Arial,Helvetica,sans-serif;color:#666;background:#eaebec;margin:15px;border:#ccc 1px solid;border-radius:3px;box-shadow:0 1px 2px #d1d1d1}
					 table th{padding:5px;border-top:1px solid #fafafa;border-bottom:1px solid #e0e0e0;background:#ededed}
					 table th{text-align:center;padding-left:10px}
					 table tr:first-child th:first-child{border-top-left-radius:3px}
					 table tr:first-child th:last-child{border-top-right-radius:3px}
					 table tr{text-align:left;padding-left:10px}
					 table td:first-child{text-align:left;padding-left:20px;border-left:0}
					 table td{padding:5px;border-top:1px solid #fff;border-bottom:1px solid #e0e0e0;border-left:1px solid #e0e0e0;background:#fafafa;white-space:nowrap}
					 table tr.even td{background:#f6f6f6}
					 table tr:last-child td{border-bottom:0}
					 table tr:last-child td:first-child{border-bottom-left-radius:3px}
					 table tr:last-child td:last-child{border-bottom-right-radius:3px}
					 table tr:hover td{background:#f2f2f2}
				 </style>
			"""
			# build message
			msg = MIMEText(('<!DOCTYPE html><html><head><meta charset=\'UTF-8\' />'+styles+'</head><body>'+message+'</body></html>').encode("utf-8"), 'html', 'utf-8')
			msg['Subject'] = subject
			msg['From']    = self.config.get('email', 'from')
			msg['To']      = self.config.get('email', 'to')

			# decide to use SSL or not
			if(self.config.get('email', 'ssl')):
				smtp_server = SMTP(self.config.get('email', 'server'))
			else:
				smtp_server = SMTP(self.config.get('email', 'server'))

			smtp_server.set_debuglevel(False)
			smtp_server.login(self.config.get('email', 'user'), self.config.get('email', 'pass'))

			# attempt to send message
			try:
				smtp_server.sendmail(self.config.get('email', 'from'), self.config.get('email', 'to'), msg.as_string())
			finally:
				smtp_server.close()
		except (Exception, exc):
			if (self.debug):
				print("Failed to send email: ", str(exc))
			return False
		return True