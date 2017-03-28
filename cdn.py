def dig_cdn(url):
	import dns.resolver
	import requests
	import re

	try:
		if not url.startswith('http'):
			url = "http://" + url
		html = requests.get(url).text
	except:
		return "Invalid url"
	
	name = url[:url.find(".")]

	link_re = re.compile('://.*?/')
	links = link_re.findall(html)
	
	def adjust(url):
		"""Adjust urls extracted using regex, correct for extraction errors.
		e.g. ://ssl.bbc.co.uk\' : \'http://www.bbc.co.uk\')+\'/wwscripts/flag" """
		if url.startswith("://"):
			url = url[3:]
		if url.find("/") != -1:
			url = url[:url.find("/")]
		if url.find("?") != -1:
			url = url[:url.find("?")]
		if url.find(" ") != -1:
			url = url[:url.find(" ")]
		if url.find("'") != -1:
			url = url[:url.find("'")]
		if url.find('"') != -1:
			url = url[:url.find('"')]
		if url.startswith("www"):
			url = url[4:]
		
		return url

	def cdn_lookup(answer):
		#Look for CDN provider within a url or a DNS response.
		cdn = ""

		if "akamai" in answer:
			cdn += "Akamai "
		if "cloudfront" in answer:
			cdn += "Cloudfront "
		if "cdn77" in answer:
			cdn += "CDN77 "
		if "netdna" in answer:
			cdn += "MaxCDN "
		if "fastly" in answer:
			cdn += "Fastly "
		if "cdngc" in answer:
			cdn += "CDNetworks "

		return cdn.rstrip()

	def query_dns(url):
		try:
			answer = dns.resolver.query(url).rrset.to_text()
		except:
			answer = ""

		return answer

	links = map(adjust, links)

	#Count the frequency of links on a page
	link_set = {}
	for url in links:
		if name in url or cdn_lookup(url):
			if url in link_set:
				link_set[url] += 1
			else:
				link_set[url] = 1

	#Filter links that appears more than once
	links = []
	for url, frequency in link_set.items():
		if frequency > 1 and re.search("([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?", url):
			links.append(url)

	link_set = None

	#Query for DNS records. Join list to a single string.
	answer = "\n".join(list(map(query_dns,links)))

	return cdn_lookup(answer)

if __name__ == '__main__':
	import sys
	output = dig_cdn(sys.argv[1])
	if output == "":
		output = "No CDN provider was found."
	print output