package com.tsb.web.util;

import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class CookieManager {
	private HttpServletRequest request;
	private HttpServletResponse response;

	public CookieManager(HttpServletRequest req, HttpServletResponse res) {
		request = req;
		response = res;
	}

	public String getCookieValue(String name) {
		Cookie[] cookies = request.getCookies();
		if (cookies == null)
			return null;

		Cookie cookie = null;
		for (int i = 0; i < cookies.length; i++) {
			cookie = cookies[i];
			if (cookie.getName().equalsIgnoreCase(name)) {
				return cookie.getValue();
			}
		}
		return null;
	}

	public void setCookie(String name, String value, String domain, int expire) {
		setCookie(name, value, domain, "/", expire);
	}

	public void setCookie(String name, String value, String domain,
			String path, int expire) {
		Cookie cookie = new Cookie(name, value);
		cookie.setDomain(domain);
		cookie.setPath(path);
		if (expire >= 0) {
			cookie.setMaxAge(expire);
		}
		response.addCookie(cookie);
	}

	public void setCookie(String name, String value, String domain) {
		setCookie(name, value, domain, -1);
	}

	public void clearCookie(String name, String domain) {
		setCookie(name, "", domain, 0);
	}

	public void setRequestAttribute(String name, String value) {
		request.setAttribute(name, value);
	}
}
