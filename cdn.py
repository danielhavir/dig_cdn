def adjust(url):
	"""Adjust urls extracted using regex, correct for extraction errors.
	e.g. ://ssl.bbc.co.uk\' : \'http://www.bbc.co.uk\')+\'/wwscripts/flag" """
	if url.find("//") != -1:
		url = url[url.find("//")+2:]
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

def dig_cdn(url):
	import dns.resolver
	import requests
	import re

	try:
		if not url.startswith('http'):
			url = "http://" + url
		r = requests.get(url)
	except:
		return "Invalid url"
	
	html = r.text
	name = adjust(url)
	name = name[:name.find(".")]

	link_re = re.compile('//.*?/')
	links = link_re.findall(html)

	def query_dns(url):
		try:
			answer = dns.resolver.query(url).rrset.to_text()
		except:
			answer = ""

		return answer

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
			cdn += "MaxCDN/StackPath "
		if "hwcdn" in answer:
			cdn += "Highwinds/StackPath "
		if "fastly" in answer:
			cdn += "Fastly "
		if "cdngc" in answer:
			cdn += "CDNetworks "
		if "cloudflare" in answer:
			cdn += "Cloudflare "

		return cdn.rstrip()

	links = map(adjust, links)

	#Iterate through all links found on the main page and filter for links with domain name
	link_set = set()
	for url in links:
		if name in url or cdn_lookup(url):
			link_set.add(url)

	#Query for DNS records. Join list to a single string.
	answer = "\n".join(list(map(query_dns,link_set)))

	return cdn_lookup(answer)

if __name__ == '__main__':
	import sys
	output = dig_cdn(sys.argv[1])
	if output == "":
		output = "No CDN Provider found."
	print output