package com.tsb.web.controller.proxy;

import java.sql.Timestamp;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import com.crawler.dao.read.ProxyTYCReadDao;
import com.crawler.dao.write.ProxyTYCWriteDao;
import com.crawler.model.ProxyTYC;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.tsb.web.controller.BaseController;

@Controller
@RequestMapping(value = "/api/admin/proxy")
@SuppressWarnings(value = { "rawtypes", "unchecked" })
public class ProxyCtrl extends BaseController {
	@Autowired
	private ProxyTYCReadDao proxyTYCReadDao;
	
	@Autowired
	private ProxyTYCWriteDao proxyTYCWriteDao;

	@RequestMapping(value = "/tyc/count", method = RequestMethod.GET)
	@ResponseBody
	public Map countTYCProxy() throws Exception {
		int cnt = proxyTYCReadDao.count();
		Map map = new HashMap();
		map.put("code", 0);
		map.put("count", cnt);
		return map;
	}
	
	@RequestMapping(value = "/tyc/add", method = RequestMethod.POST)
	@ResponseBody
	public Map addTYCProxy(@RequestBody String jsonRequest) throws Exception {
		System.out.println(jsonRequest);
		ObjectMapper mapper = new ObjectMapper();
		Map<String, Object> data = (Map<String, Object>) mapper.readValue(jsonRequest, Map.class);
		String ip = (String)data.get("ip");
		Integer port = (Integer)data.get("port");
		String type = (String)data.get("type");
		ProxyTYC p = proxyTYCReadDao.get(ip, port, type);
		if( p == null ){
			p = new ProxyTYC();
			p.setIp(ip);
			p.setPort(port);
			p.setType(type);
			p.setCreateTime(new Timestamp((new Date()).getTime()));
			proxyTYCWriteDao.insert(p);
		}
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}

}
