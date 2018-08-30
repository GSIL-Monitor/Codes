package com.tsb.web.controller;

import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.dao.read.LocationReadDao;
import com.tsb.util.RequestVO;

@Controller
@RequestMapping(value = "/api/company/location")
@SuppressWarnings({ "rawtypes", "unchecked" })
public class LocationCtrl extends BaseController {
	@Autowired
	private LocationReadDao locationReadDao;

	@RequestMapping(value = "/get", method = RequestMethod.POST)
	@ResponseBody
	public Map get(@RequestBody RequestVO request) {
		int id = (int) request.getPayload().get("id");
		String name = locationReadDao.get(id);
		Map map = new HashMap();
		map.put("name", name);
		map.put("code", 0);
		return map;

	}
	
	@RequestMapping(value = "/getByName", method = RequestMethod.POST)
	@ResponseBody
	public Map getByName(@RequestBody RequestVO request) {
		String name = (String) request.getPayload().get("name");
		int id= locationReadDao.getByName(name);
		Map map = new HashMap();
		map.put("id", id);
		map.put("code", 0);
		return map;

	}
}
